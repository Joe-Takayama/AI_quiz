from django.shortcuts import render, redirect
from django.views import View


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