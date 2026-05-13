import logging
from collections import Counter
from celery import shared_task
from django.db import transaction
from django.db.models import F

from apps.paragraphs.models import Paragraph, ParagraphWordFrequency, WordFrequency

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def process_paragraph_text(self, paragraph_id):
    # tokenize paragraph, count words, and update global/local frequencies idempontently
    try:
        paragraph = Paragraph.objects.select_related("user").get(pk=paragraph_id)
    except Paragraph.DoesNotExist:
        logger.warning("process_paragraph_text: Paragraph %s not found — skipping.", paragraph_id)
        return

    # split on whitespace, lowercase, then strip surrounding punctuation from
    # each token so that "hello," and "hello" are counted as the same word
    STRIP_CHARS = ".,!?;:\"'()-"
    tokens = [
        token.lower().strip(STRIP_CHARS)
        for token in paragraph.content.split()
    ]
    # discard empty strings that may result after stripping
    tokens = [t for t in tokens if t]


    new_counts = Counter(tokens)  # {word: count_in_this_paragraph}

    with transaction.atomic():
        # fetch existing counts to calculate delta for idempotent re-processing
        existing_pwf = {
            pwf.word: pwf.count
            for pwf in ParagraphWordFrequency.objects.filter(paragraph=paragraph)
        }

        # upsert paragraphwordfrequency
        for word, count in new_counts.items():
            ParagraphWordFrequency.objects.update_or_create(
                paragraph=paragraph,
                word=word,
                defaults={"count": count},
            )

        # remove paragraphwordfrequency rows for words no longer present
        stale_words = set(existing_pwf.keys()) - set(new_counts.keys())
        if stale_words:
            ParagraphWordFrequency.objects.filter(
                paragraph=paragraph, word__in=stale_words
            ).delete()

        # update global wordfrequency for the user across all changed words
        all_words = set(new_counts.keys()) | set(existing_pwf.keys())

        for word in all_words:
            old_count = existing_pwf.get(word, 0)
            new_count = new_counts.get(word, 0)
            delta = new_count - old_count  # calculate delta for idempotent update

            if delta == 0:
                continue  # no change

            wf_obj, created = WordFrequency.objects.get_or_create(
                user=paragraph.user,
                word=word,
                defaults={"frequency": 0},
            )

            if created:
                # brand-new global entry — set directly to avoid an extra update
                wf_obj.frequency = new_count
                wf_obj.save(update_fields=["frequency"])
            else:
                # use f() expression to avoid race conditions between workers
                WordFrequency.objects.filter(pk=wf_obj.pk).update(
                    frequency=F("frequency") + delta
                )

    logger.info(
        "process_paragraph_text: processed paragraph %s — %d unique tokens.",
        paragraph_id,
        len(new_counts),
    )


@shared_task
def cleanup_zero_frequency_words():
    # periodic task to remove wordfrequency rows whose count has dropped to zero
    deleted_count, _ = WordFrequency.objects.filter(frequency__lte=0).delete()
    logger.info(
        "cleanup_zero_frequency_words: removed %d stale WordFrequency row(s).",
        deleted_count,
    )
    return deleted_count
