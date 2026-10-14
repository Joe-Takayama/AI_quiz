from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views import View

from .forms import SignUpForm, LoginForm


# ==========================
# 新規登録
# ==========================

class SignUpView(View):

    def get(self, request):

        form = SignUpForm()

        return render(request, 'accounts/signup.html', {'form': form})

    def post(self, request):

        form = SignUpForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect('quizapp:index')
        return render(request, 'accounts/signup.html', {'form': form})


# ==========================
# ログイン
# ==========================

class LoginView(View):

    def get(self, request):

        form = LoginForm()

        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):

        form = LoginForm(request.POST)

        if form.is_valid():

            email = form.changed_data['email']
            password = form.changed_data['password']

            try:
                user = User.objects.get(email__iexact=email)

            except (User.DoesNotExist, User.MultipleObjectsReturned):
                user = None

                if user is not None:

                    user = authenticate(request, username=user.username, password=password)

                if user is not None:

                    login(request, user)

                    return redirect('quizapp:index')

                form.add_error(None, 'メールアドレスまたはパスワードが正しくありません。')

        return render(request, 'accounts/login.html', {'form': form})


# ============================
# ログアウト
# ============================

class LogoutView(View):

    def post(self, request):

        logout(request)

        return redirect('quizapp:index')