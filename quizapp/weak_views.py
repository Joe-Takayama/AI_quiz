from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View

from .forms import WeakPracticeForm

from .services.ai import QuizGenerationError

from .services.weakness import (
    get_weak_themes,
    generate_weak_questions,
)

from .views import create_attempt


@method_decorator(login_required, name='dispatch')
class WeakPracticeView(View):

    # ====================================
    # 苦手候補の一覧
    # ====================================

    def get(self, request):

        candidates = get_weak_themes(
            request.user
        )

        form = WeakPracticeForm(
            candidates=candidates,
        )

        return self.render_page(
            request,
            candidates,
            form,
        )

    # ====================================
    # 選んだテーマの追加問題を生成
    # ====================================

    def post(self, request):

        # 送信時にも本人の履歴から候補を確認する。
        candidates = get_weak_themes(
            request.user
        )

        form = WeakPracticeForm(
            request.POST,
            candidates=candidates,
        )

        if form.is_valid():

            topic = form.cleaned_data['topic']

            candidate = next(
                item
                for item in candidates
                if item['key'] == topic
            )

            selected = {
                'field': candidate['field'],
                'theme': candidate['theme'],
                'difficulty': 'beginner',
                'question_count': 5,
            }

            try:

                questions = generate_weak_questions(
                    request.user,
                    selected,
                )

            except QuizGenerationError as exc:

                form.add_error(
                    None,
                    str(exc),
                )

            else:

                attempt = create_attempt(
                    request,
                    selected,
                    questions,
                )

                return redirect(
                    'quizapp:question',
                    attempt_id=attempt.pk,
                )

        return self.render_page(
            request,
            candidates,
            form,
        )

    def render_page(
        self,
        request,
        candidates,
        form,
    ):

        return render(
            request,
            'quizapp/weak_practice.html',
            {
                'candidates': candidates,
                'form': form,
            },
        )