import uuid

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Sum
from django.http import Http404
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View

from .forms import QuizSettingsForm
from .learning import (
    get_learning_question,
    sync_learning_questions,
)
from .models import QuizAttempt, LearningQuestion
from .quiz_config import QUIZ_FIELDS
from .services.ai import (
    generate_questions,
    QuizGenerationError,
)


# ====================================
# クイズの挑戦記録を作成
# ====================================

def create_attempt(request, selected, questions):

    if 'quiz_owner' not in request.session:

        request.session['quiz_owner'] = uuid.uuid4().hex

    return QuizAttempt.objects.create(
        user=(
            request.user
            if request.user.is_authenticated
            else None
        ),
        session_token=request.session['quiz_owner'],
        questions=questions,
        **selected,
    )


# ====================================
# 自分のクイズだけ取得
# ====================================

class QuizAccessMixin:

    def get_attempt(
        self,
        request,
        attempt_id,
        lock=False,
    ):

        token = request.session.get('quiz_owner')

        allowed = Q(pk__in=[])

        if token:

            allowed |= Q(
                user__isnull=True,
                session_token=token,
            )

        if request.user.is_authenticated:

            allowed |= Q(user=request.user)

        queryset = QuizAttempt.objects.filter(allowed)

        if lock:

            queryset = queryset.select_for_update()

        return get_object_or_404(
            queryset,
            pk=attempt_id,
        )


# ====================================
# TOP画面
# ====================================

class IndexView(View):

    def get(self, request):

        total = 0
        correct = 0
        review_count = 0

        if request.user.is_authenticated:

            stats = QuizAttempt.objects.filter(
                user=request.user,
                completed_at__isnull=False,
            ).aggregate(
                total=Sum('question_count'),
                correct=Sum('correct_count'),
            )

            total = stats['total'] or 0
            correct = stats['correct'] or 0

            # 通常クイズの履歴を復習用データへ反映する。
            sync_learning_questions(request.user)

            # 復習して正解した問題は、この件数から外れる。
            review_count = LearningQuestion.objects.filter(
                user=request.user,
                needs_review=True,
            ).count()

        context = {
            'answered_count': total,

            'accuracy': (
                round(correct / total * 100, 1)
                if total
                else 0
            ),

            'review_count': review_count,
        }

        return render(
            request,
            'quizapp/index.html',
            context,
        )


# ====================================
# 出題条件選択画面
# ====================================

class QuizSettingsView(View):

    def get(self, request):

        field = request.GET.get('field', 'python')

        if field not in QUIZ_FIELDS:

            field = 'python'

        first_theme = QUIZ_FIELDS[field]['themes'][0][0]

        form = QuizSettingsForm(
            initial={
                'field': field,
                'theme': first_theme,
                'difficulty': 'beginner',
                'question_count': 5,
            }
        )

        return self.render_page(request, form)

    def post(self, request):

        form = QuizSettingsForm(request.POST)

        if form.is_valid():

            try:

                questions = generate_questions(
                    form.cleaned_data
                )

            except QuizGenerationError as exc:

                form.add_error(None, str(exc))

            else:

                attempt = create_attempt(
                    request,
                    form.cleaned_data,
                    questions,
                )

                return redirect(
                    'quizapp:question',
                    attempt_id=attempt.pk,
                )

        return self.render_page(request, form)

    def render_page(self, request, form):

        return render(
            request,
            'quizapp/quiz_settings.html',
            {
                'form': form,
                'quiz_fields': QUIZ_FIELDS,
            },
        )


# ====================================
# 問題・回答
# ====================================

class QuestionView(QuizAccessMixin, View):

    def get(self, request, attempt_id):

        attempt = self.get_attempt(
            request,
            attempt_id,
        )

        if attempt.completed_at:

            return redirect(
                'quizapp:result',
                attempt_id=attempt.pk,
            )

        index = len(attempt.answers)

        question = attempt.questions[index]

        # 回答前の画面に正解・解説を渡さない。
        public_question = {
            'text': question['text'],
            'code': question.get('code', ''),
        }

        options = [
            {
                'value': i,
                'label': 'ABCD'[i],
                'text': text,
            }
            for i, text
            in enumerate(question['choices'])
        ]

        return render(
            request,
            'quizapp/question.html',
            {
                'attempt': attempt,
                'question': public_question,
                'options': options,
                'index': index,
                'number': index + 1,

                'progress': round(
                    (index + 1)
                    / attempt.question_count
                    * 100
                ),
            },
        )

    def post(self, request, attempt_id):

        with transaction.atomic():

            attempt = self.get_attempt(
                request,
                attempt_id,
                lock=True,
            )

            if attempt.completed_at:

                return redirect(
                    'quizapp:result',
                    attempt_id=attempt.pk,
                )

            try:

                choice = int(
                    request.POST.get('choice', '')
                )

                index = int(
                    request.POST.get(
                        'question_index',
                        '',
                    )
                )

            except (TypeError, ValueError):

                return redirect(
                    'quizapp:question',
                    attempt_id=attempt.pk,
                )

            # 古い回答の再送で、次の問題を回答済みにしない。
            if (
                choice not in range(4)
                or index != len(attempt.answers)
            ):

                return redirect(
                    'quizapp:question',
                    attempt_id=attempt.pk,
                )

            old_answers = attempt.answers

            new_answers = [
                *old_answers,
                choice,
            ]

            correct_count = attempt.correct_count
            completed_at = attempt.completed_at

            if len(new_answers) == attempt.question_count:

                correct_count = sum(
                    answer == question['correct_index']
                    for answer, question in zip(
                        new_answers,
                        attempt.questions,
                    )
                )

                completed_at = timezone.now()

            # 同じ状態からの二重更新を防ぐ。
            updated = QuizAttempt.objects.filter(
                pk=attempt.pk,
                answers=old_answers,
                completed_at__isnull=True,
            ).update(
                answers=new_answers,
                correct_count=correct_count,
                completed_at=completed_at,
            )

            if not updated:

                return redirect(
                    'quizapp:question',
                    attempt_id=attempt.pk,
                )

        return redirect(
            'quizapp:explanation',
            attempt_id=attempt.pk,
            number=index + 1,
        )


# ====================================
# 正誤・解説
# ====================================

class ExplanationView(QuizAccessMixin, View):

    def get(
        self,
        request,
        attempt_id,
        number,
    ):

        attempt = self.get_attempt(
            request,
            attempt_id,
        )

        if not 1 <= number <= len(attempt.answers):

            raise Http404

        question = attempt.questions[number - 1]
        answer = attempt.answers[number - 1]

        can_favorite = (
            request.user.is_authenticated
            and attempt.user_id == request.user.pk
        )

        is_favorite = False

        if can_favorite:

            learning_question = get_learning_question(
                request.user,
                attempt,
                number - 1,
            )

            is_favorite = learning_question.is_favorite

        context = {
            'attempt': attempt,
            'question': question,
            'number': number,

            'is_correct': (
                answer == question['correct_index']
            ),

            'your_answer': question['choices'][answer],

            'correct_answer': question['choices'][
                question['correct_index']
            ],

            'can_favorite': can_favorite,
            'is_favorite': is_favorite,
        }

        return render(
            request,
            'quizapp/explanation.html',
            context,
        )


# ====================================
# 結果画面
# ====================================

class ResultView(QuizAccessMixin, View):

    def get(self, request, attempt_id):

        attempt = self.get_attempt(
            request,
            attempt_id,
        )

        if not attempt.completed_at:

            return redirect(
                'quizapp:question',
                attempt_id=attempt.pk,
            )

        rows = [
            {
                'number': i + 1,

                'correct': (
                    answer == question['correct_index']
                ),
            }
            for i, (question, answer) in enumerate(
                zip(
                    attempt.questions,
                    attempt.answers,
                )
            )
        ]

        return render(
            request,
            'quizapp/result.html',
            {
                'attempt': attempt,
                'rows': rows,
            },
        )


# ====================================
# 同じ問題へもう一度挑戦
# ====================================

class RetryView(QuizAccessMixin, View):

    def post(self, request, attempt_id):

        old = self.get_attempt(
            request,
            attempt_id,
        )

        if not old.completed_at:

            return redirect(
                'quizapp:question',
                attempt_id=old.pk,
            )

        selected = {
            name: getattr(old, name)
            for name in [
                'field',
                'theme',
                'difficulty',
                'question_count',
            ]
        }

        attempt = create_attempt(
            request,
            selected,
            old.questions,
        )

        return redirect(
            'quizapp:question',
            attempt_id=attempt.pk,
        )


# ====================================
# 学習履歴画面
# ====================================

@method_decorator(login_required, name='dispatch')
class HistoryView(View):

    def get(self, request):

        attempts = QuizAttempt.objects.filter(
            user=request.user,
            completed_at__isnull=False,
        )

        return render(
            request,
            'quizapp/history.html',
            {
                'attempts': attempts,
            },
        )