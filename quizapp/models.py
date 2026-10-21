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



# ====================================
# 復習・お気に入りの問題
# ====================================

class LearningQuestion(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_questions',
    )

    fingerprint = models.CharField(max_length=64)

    field = models.CharField(max_length=40)
    theme = models.CharField(max_length=40)
    difficulty = models.CharField(max_length=20)

    question = models.JSONField()

    needs_review = models.BooleanField(default=False)

    last_answer = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    last_answered_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    is_favorite = models.BooleanField(default=False)

    favorited_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'fingerprint'],
                name='unique_user_learning_question',
            ),
        ]

    @property
    def field_label(self):
        return QUIZ_FIELDS[self.field]['label']

    @property
    def theme_label(self):
        return dict(
            QUIZ_FIELDS[self.field]['themes']
        ).get(self.theme, self.theme)

    @property
    def difficulty_label(self):
        return dict(DIFFICULTIES).get(
            self.difficulty,
            self.difficulty,
        )

    @property
    def previous_answer(self):

        if self.last_answer is None:
            return ''

        return self.question['choices'][self.last_answer]


# ====================================
# 復習・お気に入りからの再挑戦
# ====================================

class LearningRun(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    mode = models.CharField(
        max_length=10,
        choices=[
            ('review', '復習'),
            ('favorite', 'お気に入り'),
        ],
    )

    items = models.JSONField(default=list)

    answers = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)