import uuid
from django.db import models
from django.conf import settings


class Paragraph(models.Model):
    # stores a raw paragraph of text submitted by a user

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="paragraphs",
    )
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def word_count(self, word):
        # return the number of times a given word appears in the paragraph content
        target = word.lower()
        return sum(1 for w in self.content.lower().split() if w == target)

    def __str__(self):
        return f"{self.user} — {self.content[:60]}"

    class Meta:
        ordering = ["-created_date"]


class WordFrequency(models.Model):
    # tracks the total frequency of a word across all paragraphs for a given user

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="word_frequencies",
    )
    word = models.CharField(max_length=100)
    frequency = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        # normalise word to lowercase before saving
        self.word = self.word.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} — '{self.word}': {self.frequency}"

    class Meta:
        unique_together = ("user", "word")
        ordering = ["-frequency"]


class ParagraphWordFrequency(models.Model):
    # tracks the occurrence count of a specific word within a single paragraph

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paragraph = models.ForeignKey(
        Paragraph,
        on_delete=models.CASCADE,
        related_name="word_counts",
    )
    word = models.CharField(max_length=100)
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Paragraph({self.paragraph_id}) — '{self.word}': {self.count}"

    class Meta:
        unique_together = ("paragraph", "word")
        ordering = ["-count"]
