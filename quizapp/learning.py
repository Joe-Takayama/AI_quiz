import hashlib
import json

from .models import LearningQuestion, QuizAttempt


def get_learning_question(user, attempt, index):

    question = attempt.questions[index]

    source = {
        'field': attempt.field,
        'theme': attempt.theme,
        'difficulty': attempt.difficulty,
        'question': question,
    }

    serialized = json.dumps(
        source,
        ensure_ascii=False,
        sort_keys=True,
    )

    fingerprint = hashlib.sha256(
        serialized.encode('utf-8')
    ).hexdigest()

    item, _ = LearningQuestion.objects.get_or_create(
        user=user,
        fingerprint=fingerprint,
        defaults={
            'field': attempt.field,
            'theme': attempt.theme,
            'difficulty': attempt.difficulty,
            'question': question,
        },
    )

    return item


def sync_learning_questions(user):

    attempts = QuizAttempt.objects.filter(
        user=user,
        completed_at__isnull=False,
    ).order_by('completed_at', 'pk')

    for attempt in attempts.iterator():

        for index, answer in enumerate(attempt.answers):

            item = get_learning_question(
                user,
                attempt,
                index,
            )

            # 復習後の新しい回答を、古い履歴で上書きしない。
            if (
                item.last_answered_at is not None
                and item.last_answered_at >= attempt.completed_at
            ):
                continue

            item.last_answer = answer

            item.needs_review = (
                answer
                != attempt.questions[index]['correct_index']
            )

            item.last_answered_at = attempt.completed_at

            item.save(
                update_fields=[
                    'last_answer',
                    'needs_review',
                    'last_answered_at',
                ]
            )