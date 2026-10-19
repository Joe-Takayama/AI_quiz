import uuid

from django.conf import settings
from django.db import models

from .quiz_config import QUIZ_FIELDS, DIFFICULTIES


class QuizAttempt(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    session_token = models.CharField(
        max_length=32,
    )

    field = models.CharField(
        max_length=40,
    )

    theme = models.CharField(
        max_length=40,
    )

    difficulty = models.CharField(
        max_length=20,
    )

    question_count = models.PositiveSmallIntegerField()

    questions = models.JSONField(
        default=list,
    )

    answers = models.JSONField(
        default=list,
    )

    correct_count = models.PositiveSmallIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:

        ordering = ['-created_at']

    @property
    def accuracy(self):

        if not self.question_count:
            return 0

        return round(
            self.correct_count
            / self.question_count
            * 100,
            1,
        )

    @property
    def field_label(self):

        return QUIZ_FIELDS[self.field]['label']

    @property
    def theme_label(self):

        themes = dict(
            QUIZ_FIELDS[self.field]['themes']
        )

        return themes[self.theme]

    @property
    def difficulty_label(self):

        return dict(DIFFICULTIES)[self.difficulty]