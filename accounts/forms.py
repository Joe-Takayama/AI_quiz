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

        email = self.changed_data['email'].strip().lower()

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
        widget=forms.PasswordInput(
            attrs={
                'class': 'auth-input',
                'placeholder': 'パスワードを入力してください',
                'autocomplete': 'current-password',
            }
        ),
    )