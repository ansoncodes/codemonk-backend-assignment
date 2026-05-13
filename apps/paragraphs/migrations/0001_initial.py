import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Paragraph",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("content", models.TextField()),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("modified_date", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="paragraphs",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                "ordering": ["-created_date"],
            },
        ),
        migrations.CreateModel(
            name="WordFrequency",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("word", models.CharField(max_length=100)),
                ("frequency", models.PositiveIntegerField(default=0)),
                ("user", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="word_frequencies",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                "ordering": ["-frequency"],
                "unique_together": {("user", "word")},
            },
        ),
        migrations.CreateModel(
            name="ParagraphWordFrequency",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("word", models.CharField(max_length=100)),
                ("count", models.PositiveIntegerField(default=0)),
                ("paragraph", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="word_counts",
                    to="paragraphs.paragraph",
                )),
            ],
            options={
                "ordering": ["-count"],
                "unique_together": {("paragraph", "word")},
            },
        ),
    ]
