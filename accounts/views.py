import logging

password_reset_logger = logging.getLogger(__name__)

from smtplib import SMTPException

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)
from django.views import View

from .forms import (
    SignUpForm,
    LoginForm,
    PasswordResetForm,
    NewPasswordForm,
)


# ==========================
# 新規登録
# ==========================

class SignUpView(View):

    def get(self, request):

        form = SignUpForm()

        return render(
            request,
            'accounts/signup.html',
            {'form': form}
        )

    def post(self, request):

        form = SignUpForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect('quizapp:index')

        return render(
            request,
            'accounts/signup.html',
            {'form': form}
        )


# ==========================
# ログイン
# ==========================

class LoginView(View):

    def get(self, request):

        form = LoginForm()

        return render(
            request,
            'accounts/login.html',
            {'form': form}
        )

    def post(self, request):

        form = LoginForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(
                    email__iexact=email
                )

            except (
                User.DoesNotExist,
                User.MultipleObjectsReturned
            ):
                user = None

            if user is not None:

                user = authenticate(
                    request,
                    username=user.username,
                    password=password
                )

            if user is not None:

                login(request, user)

                return redirect('quizapp:index')

            form.add_error(
                None,
                'メールアドレスまたはパスワードが正しくありません。'
            )

        return render(
            request,
            'accounts/login.html',
            {'form': form}
        )


# ==========================
# ログアウト
# ==========================

class LogoutView(View):

    def post(self, request):

        logout(request)

        return redirect('quizapp:index')


class PasswordResetView(View):

    def get(self, request):

        form = PasswordResetForm()

        return render(
            request,
            'accounts/password_reset.html',
            {'form': form},
        )

    def post(self, request):

        form = PasswordResetForm(request.POST)

        if not form.is_valid():

            password_reset_logger.warning(
                'Password reset: invalid form'
            )

            return render(
                request,
                'accounts/password_reset.html',
                {'form': form},
            )

        email = form.cleaned_data['email'].strip()

        # 無効ユーザーも含めて、登録の一致件数を確認する。
        registered = list(
            User.objects.filter(
                email__iexact=email,
            )
        )

        eligible = [
            user
            for user in registered
            if user.is_active
            and user.has_usable_password()
        ]

        # メールアドレスやトークンはログに出さない。
        password_reset_logger.warning(
            'Password reset: matched=%s eligible=%s',
            len(registered),
            len(eligible),
        )

        sent_total = 0

        try:

            for user in eligible:

                uidb64 = urlsafe_base64_encode(
                    force_bytes(user.pk)
                )

                token = default_token_generator.make_token(
                    user
                )

                reset_path = reverse(
                    'accounts:password_reset_confirm',
                    kwargs={
                        'uidb64': uidb64,
                        'token': token,
                    },
                )

                reset_url = request.build_absolute_uri(
                    reset_path
                )

                sent_count = send_mail(
                    subject='【DataQuiz AI】パスワード再設定',
                    message=(
                        'パスワード再設定を受け付けました。\n\n'
                        '以下のリンクから新しいパスワードを'
                        '設定してください。\n\n'
                        f'{reset_url}\n\n'
                        'リンクの有効期限は1時間です。\n'
                        '心当たりがない場合は、このメールを'
                        '破棄してください。'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )

                password_reset_logger.warning(
                    'Password reset: backend_sent=%s',
                    sent_count,
                )

                if sent_count != 1:
                    raise SMTPException(
                        'メール送信件数が1件ではありません。'
                    )

                sent_total += sent_count

        except (SMTPException, OSError) as exc:

            password_reset_logger.warning(
                'Password reset: failed=%s',
                type(exc).__name__,
            )

            form.add_error(
                None,
                'メールを送信できませんでした。'
                '時間をおいて再度お試しください。',
            )

            return render(
                request,
                'accounts/password_reset.html',
                {'form': form},
            )

        password_reset_logger.warning(
            'Password reset: finished sent_total=%s',
            sent_total,
        )

        return redirect(
            'accounts:password_reset_done'
        )


# ========================================
# メール送信後の案内
# ========================================

class PasswordResetDoneView(View):

    def get(self, request):

        return render(
            request,
            'accounts/password_reset_done.html'
        )


# ========================================
# 新しいパスワードの設定
# ========================================

class PasswordResetConfirmView(View):

    def get_user(self, uidb64):

        try:

            user_id = force_str(
                urlsafe_base64_decode(uidb64)
            )

            user = User.objects.get(
                pk=user_id,
                is_active=True
            )

            if not user.has_usable_password():
                return None

            return user

        except (
            User.DoesNotExist,
            ValueError,
            TypeError,
            OverflowError
        ):
            return None

    def get(self, request, uidb64, token):

        user = self.get_user(uidb64)

        # リンクが有効なら入力画面を表示する。
        if (
            user is not None
            and default_token_generator.check_token(user, token)
        ):

            form = NewPasswordForm(user=user)

            return render(
                request,
                'accounts/password_reset_confirm.html',
                {
                    'form': form,
                    'validlink': True,
                }
            )

        return render(
            request,
            'accounts/password_reset_confirm.html',
            {'validlink': False}
        )

    def post(self, request, uidb64, token):

        user = self.get_user(uidb64)

        # 送信時にもリンクを確認する。
        if (
            user is None
            or not default_token_generator.check_token(user, token)
        ):

            return render(
                request,
                'accounts/password_reset_confirm.html',
                {'validlink': False}
            )

        form = NewPasswordForm(
            request.POST,
            user=user
        )

        if form.is_valid():

            password = form.cleaned_data['new_password1']

            # パスワードをハッシュ化して保存する。
            user.set_password(password)

            user.save()

            return redirect('accounts:password_reset_complete')

        return render(
            request,
            'accounts/password_reset_confirm.html',
            {
                'form': form,
                'validlink': True,
            }
        )


# ========================================
# パスワード変更完了
# ========================================

class PasswordResetCompleteView(View):

    def get(self, request):

        return render(
            request,
            'accounts/password_reset_complete.html'
        )