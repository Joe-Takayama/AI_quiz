from django import forms

from .quiz_config import (
    QUIZ_FIELDS,
    DIFFICULTIES,
    QUESTION_COUNTS,
)


class QuizSettingsForm(forms.Form):

    source_mode = forms.ChoiceField(
        label='出題方法',

        choices=[
            ('normal', '通常のAI出題'),
            ('material', '教材から出題'),
        ],

        initial='normal',

        widget=forms.Select(
            attrs={
                'class': 'settings-select',
            },
        ),
    )

    field = forms.ChoiceField(
        label='分野',

        choices=[
            (key, value['label'])
            for key, value in QUIZ_FIELDS.items()
        ],

        widget=forms.Select(
            attrs={
                'class': 'settings-select',
            }
        ),
    )

    theme = forms.ChoiceField(
        label='テーマ',

        choices=[],

        widget=forms.Select(
            attrs={
                'class': 'settings-select',
            }
        ),
    )

    difficulty = forms.ChoiceField(
        label='難易度',

        choices=DIFFICULTIES,

        widget=forms.RadioSelect(),

        initial='beginner',
    )

    question_count = forms.TypedChoiceField(
        label='問題数',

        choices=QUESTION_COUNTS,

        coerce=int,

        widget=forms.RadioSelect(),

        initial=5,
    )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        if self.is_bound:

            selected_field = self.data.get('field')

        else:

            selected_field = self.initial.get(
                'field',
                'python',
            )

        field_config = QUIZ_FIELDS.get(
            selected_field,
            {},
        )

        self.fields['theme'].choices = (
            field_config.get('themes', [])
        )


# ====================================
# 解説画面からAIに質問するフォーム
# ====================================

class AIQuestionForm(forms.Form):

    question = forms.CharField(
        label='この問題についてAIに質問',

        max_length=1000,

        strip=True,

        widget=forms.Textarea(
            attrs={
                'class': 'ai-question-input',
                'rows': 3,
                'placeholder': (
                    '例：appendの使い方を'
                    '具体例で教えてください'
                ),
                'maxlength': 1000,
            },
        ),

        error_messages={
            'required': '質問を入力してください。',
            'max_length': (
                '質問は1000文字以内で入力してください。'
            ),
        },
    )


# ====================================
# 苦手テーマの追加問題
# ====================================

class WeakPracticeForm(forms.Form):

    topic = forms.ChoiceField(
        label='復習するテーマ',
        choices=[],
        widget=forms.HiddenInput(),
        error_messages={
            'required': 'テーマを選んでください。',
            'invalid_choice': (
                'このテーマは現在の追加問題の対象ではありません。'
                '一覧を確認してください。'
            ),
        },
    )

    def __init__(
        self,
        *args,
        candidates=None,
        **kwargs,
    ):

        super().__init__(*args, **kwargs)

        self.fields['topic'].choices = [
            (
                item['key'],
                (
                    f"{item['field_label']} / "
                    f"{item['theme_label']}"
                ),
            )
            for item in (candidates or [])
        ]