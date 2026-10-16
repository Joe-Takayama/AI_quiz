from django.urls import path

from .views import IndexView, QuizSettingsView

app_name = 'quizapp'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('settings/', QuizSettingsView.as_view(), name='quiz_settings'),
]