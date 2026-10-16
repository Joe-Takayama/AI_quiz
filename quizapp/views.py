from django.shortcuts import render
from django.views import View

from .forms import QuizSettingsForm
from .quiz_config import QUIZ_FIELDS


# ==========================
# TOP画面
# ==========================

class IndexView(View):

    def get(self, request):

        context = {
            'answered_count': 0,
            'accuracy': 0,
            'review_count': 0,
        }

        return render(
            request,
            'quizapp/index.html',
            context,
        )


# ==========================
# 出題条件選択画面
# ==========================

class QuizSettingsView(View):

    def get(self, request):

        selected_field = request.GET.get(
            'field',
            'python',
        )

        if selected_field not in QUIZ_FIELDS:

            selected_field = 'python'

        first_theme = (
            QUIZ_FIELDS[selected_field]['themes'][0][0]
        )

        form = QuizSettingsForm(
            initial={
                'field': selected_field,
                'theme': first_theme,
                'difficulty': 'beginner',
                'question_count': 5,
            }
        )

        return self.render_page(
            request,
            form,
        )

    def post(self, request):

        form = QuizSettingsForm(
            request.POST
        )

        if form.is_valid():

            request.session['quiz_settings'] = (
                form.cleaned_data
            )

            # 次の工程で、ここに問題生成と
            # 問題画面への遷移を追加する。

            return self.render_page(
                request,
                form,
                settings_saved=True,
            )

        return self.render_page(
            request,
            form,
        )

    def render_page(
        self,
        request,
        form,
        settings_saved=False,
    ):

        context = {
            'form': form,
            'quiz_fields': QUIZ_FIELDS,
            'settings_saved': settings_saved,
        }

        return render(
            request,
            'quizapp/quiz_settings.html',
            context,
        )