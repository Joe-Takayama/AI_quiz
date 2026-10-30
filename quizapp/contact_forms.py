from django import forms


class ContactForm(forms.Form):

    name = forms.CharField(
        label='お名前',
        max_length=100,
        strip=True,
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'name',
                'placeholder': '例：山田 太郎',
            },
        ),
    )

    email = forms.EmailField(
        label='返信先メールアドレス',
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                'autocomplete': 'email',
                'placeholder': '例：example@gmail.com',
            },
        ),
        error_messages={
            'invalid': (
                '正しいメールアドレスを入力してください。'
            ),
        },
    )

    subject = forms.CharField(
        label='件名',
        max_length=200,
        strip=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': '例：クイズの解説について',
            },
        ),
    )

    message = forms.CharField(
        label='お問い合わせ内容',
        max_length=5000,
        strip=True,
        widget=forms.Textarea(
            attrs={
                'rows': 8,
                'maxlength': 5000,
                'placeholder': (
                    'お問い合わせ内容を入力してください。'
                ),
            },
        ),
    )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field in self.fields.values():

            field.widget.attrs['class'] = 'contact-input'

            field.error_messages['required'] = (
                'この項目を入力してください。'
            )

            field.error_messages['max_length'] = (
                '%(limit_value)s文字以内で入力してください。'
            )

    def clean_subject(self):

        subject = self.cleaned_data['subject']

        if '\r' in subject or '\n' in subject:

            raise forms.ValidationError(
                '件名には改行を含めないでください。'
            )

        return subject