from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from .learning import (
    get_learning_question,
    sync_learning_questions,
)
from .models import LearningQuestion, LearningRun, QuizAttempt
from .quiz_config import QUIZ_FIELDS


# ====================================
# 復習・お気に入りの一覧
# ====================================

class LearningListView(LoginRequiredMixin, View):

    mode = 'review'

    def get(self, request):

        sync_learning_questions(request.user)

        items = LearningQuestion.objects.filter(
            user=request.user,
        )

        if self.mode == 'review':

            items = items.filter(
                needs_review=True,
            ).order_by('-last_answered_at', '-pk')

        else:

            items = items.filter(
                is_favorite=True,
            ).order_by('-favorited_at', '-pk')

        selected_field = request.GET.get('field', '')

        if selected_field not in QUIZ_FIELDS:
            selected_field = ''

        if selected_field:
            items = items.filter(field=selected_field)

        return render(
            request,
            'quizapp/learning_list.html',
            {
                'mode': self.mode,
                'is_review': self.mode == 'review',
                'items': items,
                'item_count': items.count(),
                'selected_field': selected_field,
                'quiz_fields': QUIZ_FIELDS,
            },
        )


# ====================================
# 解説画面からお気に入り登録
# ====================================

class FavoriteSaveView(LoginRequiredMixin, View):

    def post(self, request, attempt_id, number):

        attempt = get_object_or_404(
            QuizAttempt,
            pk=attempt_id,
            user=request.user,
        )

        # 回答済みの問題だけ登録できる。
        if not 1 <= number <= len(attempt.answers):
            raise Http404

        item = get_learning_question(
            request.user,
            attempt,
            number - 1,
        )

        if not item.is_favorite:

            item.is_favorite = True
            item.favorited_at = timezone.now()

            item.save(
                update_fields=[
                    'is_favorite',
                    'favorited_at',
                ]
            )

        messages.success(
            request,
            'お気に入りに保存しました。',
        )

        return redirect(
            'quizapp:explanation',
            attempt_id=attempt.id,
            number=number,
        )


# ====================================
# お気に入り解除
# ====================================

class FavoriteRemoveView(LoginRequiredMixin, View):

    def post(self, request, pk):

        item = get_object_or_404(
            LearningQuestion,
            pk=pk,
            user=request.user,
        )

        item.is_favorite = False
        item.favorited_at = None

        item.save(
            update_fields=[
                'is_favorite',
                'favorited_at',
            ]
        )

        return redirect('quizapp:favorites')


# ====================================
# お気に入りの問題・解説
# ====================================

class FavoriteDetailView(LoginRequiredMixin, View):

    def get(self, request, pk):

        item = get_object_or_404(
            LearningQuestion,
            pk=pk,
            user=request.user,
            is_favorite=True,
        )

        question = item.question

        return render(
            request,
            'quizapp/learning_detail.html',
            {
                'item': item,
                'question': question,
                'correct_answer': question['choices'][
                    question['correct_index']
                ],
            },
        )


# ====================================
# 再挑戦を開始
# ====================================

class LearningStartView(LoginRequiredMixin, View):

    def post(self, request):

        mode = request.POST.get('mode')

        if mode not in ('review', 'favorite'):
            raise Http404

        sync_learning_questions(request.user)

        items = LearningQuestion.objects.filter(
            user=request.user,
        ).order_by('pk')

        if mode == 'review':

            items = items.filter(needs_review=True)
            list_url = 'quizapp:review'

        else:

            items = items.filter(is_favorite=True)
            list_url = 'quizapp:favorites'

        selected_field = request.POST.get('field', '')

        if selected_field in QUIZ_FIELDS:
            items = items.filter(field=selected_field)

        item_id = request.POST.get('item_id')

        if item_id:

            try:
                item_id = int(item_id)
            except (ValueError, TypeError):
                raise Http404

            items = items.filter(pk=item_id)

        snapshots = [
            {
                'id': item.pk,
                'field_label': item.field_label,
                'theme_label': item.theme_label,
                'difficulty_label': item.difficulty_label,
                'question': item.question,
            }
            for item in items
        ]

        if not snapshots:

            messages.info(
                request,
                '再挑戦できる問題がありません。',
            )

            return redirect(list_url)

        run = LearningRun.objects.create(
            user=request.user,
            mode=mode,
            items=snapshots,
        )

        return redirect(
            'quizapp:learning_play',
            run_id=run.id,
        )


# ====================================
# 再挑戦の問題・解説・結果
# ====================================

class LearningPlayView(LoginRequiredMixin, View):

    def get_run(self, request, run_id, lock=False):

        runs = LearningRun.objects.filter(
            user=request.user,
        )

        if lock:
            runs = runs.select_for_update()

        return get_object_or_404(
            runs,
            pk=run_id,
        )

    def get(self, request, run_id):

        run = self.get_run(request, run_id)

        total = len(run.items)
        answered = len(run.answers)

        context = {
            'run': run,
            'total': total,
            'back_url': (
                'quizapp:review'
                if run.mode == 'review'
                else 'quizapp:favorites'
            ),
        }

        feedback = request.GET.get('feedback')

        if feedback is not None:

            try:
                number = int(feedback)
            except (ValueError, TypeError):
                raise Http404

            if not 1 <= number <= answered:
                raise Http404

            item = run.items[number - 1]
            question = item['question']
            answer = run.answers[number - 1]

            context.update({
                'stage': 'feedback',
                'item': item,
                'question': question,
                'number': number,
                'is_correct': (
                    answer == question['correct_index']
                ),
                'your_answer': question['choices'][answer],
                'correct_answer': question['choices'][
                    question['correct_index']
                ],
            })

        elif answered == total:

            correct_count = sum(
                answer == item['question']['correct_index']
                for item, answer in zip(
                    run.items,
                    run.answers,
                )
            )

            context.update({
                'stage': 'result',
                'correct_count': correct_count,
                'accuracy': round(
                    correct_count / total * 100,
                    1,
                ),
            })

        else:

            item = run.items[answered]
            question = item['question']

            context.update({
                'stage': 'question',
                'item': item,
                'number': answered + 1,
                'index': answered,

                # 回答前のHTMLに正解・解説を渡さない。
                'question': {
                    'text': question['text'],
                    'code': question.get('code', ''),
                },

                'options': [
                    {
                        'value': index,
                        'label': 'ABCD'[index],
                        'text': text,
                    }
                    for index, text
                    in enumerate(question['choices'])
                ],
            })

        return render(
            request,
            'quizapp/learning_play.html',
            context,
        )

    def post(self, request, run_id):

        with transaction.atomic():

            run = self.get_run(
                request,
                run_id,
                lock=True,
            )

            index = len(run.answers)

            if index >= len(run.items):

                return redirect(
                    'quizapp:learning_play',
                    run_id=run.id,
                )

            try:

                choice = int(request.POST.get('choice', ''))

                posted_index = int(
                    request.POST.get('question_index', '')
                )

            except (ValueError, TypeError):

                return redirect(
                    'quizapp:learning_play',
                    run_id=run.id,
                )

            if posted_index != index or choice not in range(4):

                return redirect(
                    'quizapp:learning_play',
                    run_id=run.id,
                )

            old_answers = run.answers
            new_answers = [*old_answers, choice]

            # 二重送信で同じ回答を追加しない。
            updated = LearningRun.objects.filter(
                pk=run.pk,
                user=request.user,
                answers=old_answers,
            ).update(answers=new_answers)

            if not updated:

                return redirect(
                    'quizapp:learning_play',
                    run_id=run.id,
                )

            snapshot = run.items[index]
            question = snapshot['question']

            LearningQuestion.objects.filter(
                pk=snapshot['id'],
                user=request.user,
            ).update(
                last_answer=choice,
                last_answered_at=timezone.now(),
                needs_review=(
                    choice != question['correct_index']
                ),
            )

        from django.urls import reverse

        url = reverse(
            'quizapp:learning_play',
            kwargs={'run_id': run.id},
        )

        return redirect(
            f'{url}?feedback={index + 1}'
        )