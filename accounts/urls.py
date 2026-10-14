from django.urls import path

from .views import (
    SignUpView,
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)


app_name = 'accounts'

urlpatterns = [
    path(
        'signup/',
        SignUpView.as_view(),
        name='signup'
    ),

    path(
        'login/',
        LoginView.as_view(),
        name='login'
    ),

    path(
        'logout/',
        LogoutView.as_view(),
        name='logout'
    ),

    path(
        'password-reset/',
        PasswordResetView.as_view(),
        name='password_reset'
    ),

    path(
        'password-reset/done/',
        PasswordResetDoneView.as_view(),
        name='password_reset_done'
    ),

    path(
        'password-reset/confirm/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),

    path(
        'password-reset/complete/',
        PasswordResetCompleteView.as_view(),
        name='password_reset_complete'
    ),
]