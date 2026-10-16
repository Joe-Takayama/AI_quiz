from django import forms

from .quiz_config import (
    QUIZ_FIELDS,
    DIFFICULTIES,
    QUESTION_COUNTS,
)


class QuizSettingsForm(forms.Form):

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