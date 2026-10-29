from django.urls import path

from .views import (
    IndexView,
    QuizSettingsView,
    QuestionView,
    ExplanationView,
    ResultView,
    RetryView,
    HistoryView,
    HintView,
    AdviceView,
)

from .learning_views import (
    LearningListView,
    FavoriteSaveView,
    FavoriteRemoveView,
    FavoriteDetailView,
    LearningStartView,
    LearningPlayView,
)

from .weak_views import WeakPracticeView


app_name = 'quizapp'


urlpatterns = [

    # TOP
    path(
        '',
        IndexView.as_view(),
        name='index',
    ),

    # 出題条件
    path(
        'settings/',
        QuizSettingsView.as_view(),
        name='quiz_settings',
    ),

    # 問題
    path(
        'question/<uuid:attempt_id>/',
        QuestionView.as_view(),
        name='question',
    ),

    # 解説
    path(
        'explanation/<uuid:attempt_id>/<int:number>/',
        ExplanationView.as_view(),
        name='explanation',
    ),

    # 結果
    path(
        'result/<uuid:attempt_id>/',
        ResultView.as_view(),
        name='result',
    ),

    # 同じ問題に再挑戦
    path(
        'retry/<uuid:attempt_id>/',
        RetryView.as_view(),
        name='retry',
    ),

    # 学習履歴
    path(
        'history/',
        HistoryView.as_view(),
        name='history',
    ),

    # 間違えた問題の復習
    path(
        'review/',
        LearningListView.as_view(mode='review'),
        name='review',
    ),

    # お気に入り一覧
    path(
        'favorites/',
        LearningListView.as_view(mode='favorite'),
        name='favorites',
    ),

    # お気に入り登録
    path(
        'favorites/save/<uuid:attempt_id>/<int:number>/',
        FavoriteSaveView.as_view(),
        name='favorite_save',
    ),

    # お気に入り解除
    path(
        'favorites/<int:pk>/remove/',
        FavoriteRemoveView.as_view(),
        name='favorite_remove',
    ),

    # 保存した問題・解説
    path(
        'favorites/<int:pk>/',
        FavoriteDetailView.as_view(),
        name='favorite_detail',
    ),

    # 復習・お気に入りから再挑戦を開始
    path(
        'learning/start/',
        LearningStartView.as_view(),
        name='learning_start',
    ),

    # 再挑戦の問題・解説・結果
    path(
        'learning/play/<uuid:run_id>/',
        LearningPlayView.as_view(),
        name='learning_play',
    ),

    # 回答前のヒント
    path(
        'hint/<uuid:attempt_id>/',
        HintView.as_view(),
        name='hint',
    ),

    # 学習結果へのアドバイス
    path(
        'advice/<uuid:attempt_id>/',
        AdviceView.as_view(),
        name='advice',
    ),

    # 苦手テーマの追加問題
    path(
        'weak-practice/',
        WeakPracticeView.as_view(),
        name='weak_practice',
    ),

]