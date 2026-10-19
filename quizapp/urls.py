from django.urls import path

from . import views


app_name = 'quizapp'


urlpatterns = [
    path(
        '',
        views.IndexView.as_view(),
        name='index',
    ),

    path(
        'settings/',
        views.QuizSettingsView.as_view(),
        name='quiz_settings',
    ),

    path(
        'question/<uuid:attempt_id>/',
        views.QuestionView.as_view(),
        name='question',
    ),

    path(
        'explanation/<uuid:attempt_id>/<int:number>/',
        views.ExplanationView.as_view(),
        name='explanation',
    ),

    path(
        'result/<uuid:attempt_id>/',
        views.ResultView.as_view(),
        name='result',
    ),

    path(
        'retry/<uuid:attempt_id>/',
        views.RetryView.as_view(),
        name='retry',
    ),

    path(
        'history/',
        views.HistoryView.as_view(),
        name='history',
    ),
]