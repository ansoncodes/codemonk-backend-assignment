from rest_framework import serializers
from django.db.models import OuterRef, Subquery, IntegerField, Value
from django.db.models.functions import Coalesce

from apps.paragraphs.models import Paragraph, ParagraphWordFrequency
from apps.paragraphs.tasks import process_paragraph_text


class ParagraphSerializer(serializers.ModelSerializer):
    # read-only serializer for paragraph model

    class Meta:
        model = Paragraph
        fields = ["id", "content", "created_date"]
        read_only_fields = fields


class ParagraphInputSerializer(serializers.Serializer):
    # accepts block text, splits it, bulk creates records, and queues celery tasks

    text = serializers.CharField(
        allow_blank=False,
        trim_whitespace=False,
        help_text="Full text input. Paragraphs must be separated by double newlines (\\n\\n).",
    )

    def validate_text(self, value):
        # ensure the submitted text contains at least one non-empty paragraph
        paragraphs = [p.strip() for p in value.split("\n\n")]
        if not any(paragraphs):
            raise serializers.ValidationError("Text must contain at least one non-empty paragraph.")
        return value

    def create(self, validated_data, user):
        # split text, bulk create objects, dispatch celery task per paragraph
        raw_text = validated_data["text"]
        # split on blank lines and discard empty segments
        raw_paragraphs = [chunk.strip() for chunk in raw_text.split("\n\n")]
        non_empty = [chunk for chunk in raw_paragraphs if chunk]
        # bulk create for a single insert query instead of n queries
        paragraph_objects = [
            Paragraph(user=user, content=chunk)
            for chunk in non_empty
        ]
        created_paragraphs = Paragraph.objects.bulk_create(paragraph_objects)
        # enqueue an async celery task for each paragraph
        for paragraph in created_paragraphs:
            process_paragraph_text.delay(str(paragraph.id))

        return created_paragraphs


class WordSearchSerializer(serializers.Serializer):
    # accepts a single word and returns top 10 paragraphs for the requesting user

    word = serializers.CharField(
        max_length=100,
        allow_blank=False,
        help_text="The word to search for across all paragraphs belonging to the authenticated user.",
    )

    def validate_word(self, value):
        # normalise the search word to lowercase before querying
        return value.lower().strip(".,!?;:\"'()-")

    def get_results(self, user):
        # query top 10 paragraphs annotated with word count using a correlated subquery to avoid n+1 issues
        word = self.validated_data["word"]
        # correlated subquery: for each paragraph row, fetch the word's count from frequency table
        word_count_subquery = Subquery(
            ParagraphWordFrequency.objects.filter(
                paragraph=OuterRef("pk"),
                word=word,
            ).values("count")[:1],
            output_field=IntegerField(),
        )

        return (
            Paragraph.objects.filter(user=user)
            # coalesce maps null (word not found) to 0 so ordering is stable
            .annotate(word_occurrence=Coalesce(word_count_subquery, Value(0)))
            .filter(word_occurrence__gt=0)          # exclude paragraphs where word is absent
            .order_by("-word_occurrence")
            .only("id", "content", "created_date")  # avoid fetching unnecessary columns
            [:10]
        )
