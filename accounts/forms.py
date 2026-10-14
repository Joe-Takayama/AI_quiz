from django.contrib.auth.password_validation import validate_password

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# ==========================
# 新規登録
# ==========================

class SignUpForm(UserCreationForm):

    password1 = forms.CharField(
        label="パスワード",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'auth-input',
                'placeholder': 'パスワードを入力してください',
                'autocomplete': 'new-password',
            }
        ),
    )

    password2 = forms.CharField(
        label='パスワード（確認）',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'auth-input',
                'placeholder': 'パスワードを再入力してください',
                'autocomplete': 'new-password',
            }
        ),
    )

    class Meta:

        model = User

        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]

        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'auth-input',
                    'placeholder': '例: 大原太郎',
                    'autocomplete': 'username',
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class': 'auth-input',
                    'placeholder': '例: example@gmail.com',
                    'autocomplete': 'email',
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['username'].label = 'ユーザー名'
        self.fields['email'].label = 'メールアドレス'
        self.fields['password1'].label = 'パスワード'
        self.fields['password2'].label = 'パスワード（確認）'

        # メールアドレスは必須とする
        self.fields['email'].required = True

    def clean_email(self):

        email = self.cleaned_data['email'].strip().lower()

        if User.objects.filter(
            email__iexact=email
        ).exists():

            raise forms.ValidationError(
                'このメールアドレスは既に登録されています。'
            )

        return email



# ==========================
# ログイン
# ==========================

class LoginForm(forms.Form):

    email = forms.EmailField(
        label='メールアドレス',
        widget=forms.EmailInput(
            attrs={
                'class': 'auth-input',
                'placeholder': '例: example@gmail.com',
                'autocomplete': 'email',
            }
        ),
    )

    password = forms.CharField(
        label='パスワード',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'auth-input',
                'placeholder': 'パスワードを入力してください',
                'autocomplete': 'current-password',
            }
        ),
    )


# ========================================
# パスワード再設定
# メールアドレス入力
# ========================================

class PasswordResetForm(forms.Form):

    email = forms.EmailField(
        label="メールアドレス",
        widget=forms.EmailInput(
            attrs={
                "class": "auth-input",
                "placeholder": "例: example@gmail.com",
                "autocomplete": "email",
            }
        ),
    )


# ========================================
# 新しいパスワード
# ========================================

class NewPasswordForm(forms.Form):

    new_password1 = forms.CharField(
        label="新しいパスワード",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "auth-input",
                "autocomplete": "new-password",
            }
        ),
    )

    new_password2 = forms.CharField(
        label="新しいパスワード（確認）",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "auth-input",
                "autocomplete": "new-password",
            }
        ),
    )

    def __init__(self, *args, user=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.user = user

    def clean(self):

        cleaned_data = super().clean()

        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2:

            if password1 != password2:

                self.add_error(
                    "new_password2",
                    "パスワードが一致していません。",
                )

            else:

                try:
                    validate_password(
                        password1,
                        user=self.user,
                    )

                except forms.ValidationError as error:

                    self.add_error(
                        "new_password1",
                        error,
                    )

        return cleaned_data