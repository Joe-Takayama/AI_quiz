import unicodedata

from django.db.models import Sum

from ..models import QuizAttempt
from ..quiz_config import QUIZ_FIELDS

from .ai import (
    generate_questions,
    QuizGenerationError,
)


# ====================================
# 苦手候補を集計する
# ====================================

def get_weak_themes(user):

    if not user.is_authenticated:
        return []

    stats = (
        QuizAttempt.objects.filter(
            user=user,
            completed_at__isnull=False,
        )
        .values('field', 'theme')
        .annotate(
            total=Sum('question_count'),
            correct=Sum('correct_count'),
        )
        .order_by('field', 'theme')
    )

    candidates = []

    for row in stats:

        field = row['field']
        theme = row['theme']

        config = QUIZ_FIELDS.get(field)

        if not config:
            continue

        themes = dict(config['themes'])

        if theme not in themes:
            continue

        total = row['total'] or 0
        correct = row['correct'] or 0

        if total < 5:
            continue

        # 丸める前の値で60％未満かを判定する。
        if correct * 100 >= total * 60:
            continue

        candidates.append({
            'key': f'{field}:{theme}',
            'field': field,
            'theme': theme,
            'field_label': config['label'],
            'theme_label': themes[theme],
            'total': total,
            'correct': correct,
            'accuracy': round(
                correct / total * 100,
                1,
            ),
        })

    candidates.sort(
        key=lambda item: (
            item['correct'] / item['total'],
            -item['total'],
            item['key'],
        )
    )

    return candidates


# ====================================
# 問題の重複確認用
# ====================================

def question_identity(question):

    return tuple(
        unicodedata.normalize(
            'NFKC',
            question.get(name, ''),
        ).strip()
        for name in ('text', 'code')
    )


# ====================================
# 過去と同じ問題を避けて新しく生成する
# ====================================

def generate_weak_questions(user, selected):

    attempts = QuizAttempt.objects.filter(
        user=user,
        field=selected['field'],
        theme=selected['theme'],
    ).only('questions')

    previous = set()

    for attempt in attempts.iterator():

        for question in attempt.questions:
            previous.add(
                question_identity(question)
            )

    # 過去と同じ問題が含まれたら、もう1回生成する。
    for _ in range(2):

        questions = generate_questions(
            selected,
            use_material=False,
        )

        if any(
            question_identity(question) in previous
            for question in questions
        ):
            continue

        return questions

    raise QuizGenerationError(
        '過去の問題と重複したため、'
        '追加問題を用意できませんでした。'
        'もう一度お試しください。'
    )