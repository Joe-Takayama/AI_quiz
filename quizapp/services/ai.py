import logging

from django.conf import settings
from google import genai
from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    model_validator,
)

from ..quiz_config import QUIZ_FIELDS, DIFFICULTIES


logger = logging.getLogger(__name__)


class QuizGenerationError(Exception):
    pass


# ==========================
# AIに返してもらう1問分の形式
# ==========================

class Question(BaseModel):

    text: str = Field(
        min_length=1,
    )

    code: str = ''

    choices: list[str] = Field(
        min_length=4,
        max_length=4,
    )

    correct_index: int = Field(
        ge=0,
        le=3,
        strict=True,
    )

    explanation: str = Field(
        min_length=1,
    )

    @model_validator(mode='after')
    def check_content(self):

        self.text = self.text.strip()

        self.explanation = (
            self.explanation.strip()
        )

        self.choices = [
            value.strip()
            for value in self.choices
        ]

        if (
            not self.text
            or not self.explanation
            or any(
                not value
                for value in self.choices
            )
        ):
            raise ValueError(
                '空の問題・選択肢・解説があります。'
            )

        if len(set(self.choices)) != 4:

            raise ValueError(
                '選択肢が重複しています。'
            )

        return self


class QuizData(BaseModel):

    questions: list[Question]


# ==========================
# 問題生成
# ==========================

def generate_questions(selected):

    if not settings.GEMINI_API_KEY:

        raise QuizGenerationError(
            'GEMINI_API_KEYを設定してください。'
        )

    field = QUIZ_FIELDS[
        selected['field']
    ]

    theme = dict(
        field['themes']
    )[
        selected['theme']
    ]

    difficulty = dict(
        DIFFICULTIES
    )[
        selected['difficulty']
    ]

    count = selected['question_count']

    prompt = f"""
日本語のデータサイエンス学習用4択クイズを作成してください。

分野: {field['label']}
テーマ: {theme}
難易度: {difficulty}
問題数: {count}問

以下の条件を守ってください。

・指定条件に合う、互いに異なる問題をちょうど{count}問作る。
・各問題の正解は必ず1つにする。
・choicesは4つの文字列にする。
・choicesにはA、B、C、Dの接頭辞を付けない。
・correct_indexは、正解の位置を0〜3で指定する。
・textには問題文を書く。
・コードが必要ならcodeにコードだけを書く。
・コードが不要ならcodeは空文字にする。
・explanationには正解の理由と誤答の理由を簡潔に書く。
・HTMLやMarkdownのコードフェンスは含めない。
・曖昧な問題を避ける。
・正解と解説が一致するか確認してから出力する。
"""

    schema = QuizData.model_json_schema()

    schema['properties']['questions'].update(
        minItems=count,
        maxItems=count,
    )

    try:

        with genai.Client(
            api_key=settings.GEMINI_API_KEY,
        ) as client:

            # 形式不正や問題数不足の場合は、
            # もう1回だけ生成を試す。
            for _ in range(2):

                response = client.interactions.create(
                    model=settings.GEMINI_MODEL,

                    input=prompt,

                    store=False,

                    response_format={
                        'type': 'text',
                        'mime_type': 'application/json',
                        'schema': schema,
                    },

                    timeout=90.0,
                )

                try:

                    data = (
                        QuizData.model_validate_json(
                            response.output_text
                        )
                    )

                    identities = {
                        (question.text, question.code)
                        for question in data.questions
                    }

                    if (
                        len(data.questions) != count
                        or len(identities) != count
                    ):
                        raise ValueError(
                            '問題数の不足または問題の重複'
                        )

                    return [
                        question.model_dump()
                        for question in data.questions
                    ]

                except (
                    ValidationError,
                    ValueError,
                    TypeError,
                ):

                    continue

    except Exception as exc:

        logger.warning(
            'Gemini generation failed: %s',
            type(exc).__name__,
        )

        raise QuizGenerationError(
            '問題を生成できませんでした。'
            'API設定・利用上限・接続状況を確認して'
            '再度お試しください。'
        ) from exc

    raise QuizGenerationError(
        '指定した形式で問題を作れませんでした。'
        'もう一度お試しください。'
    )