import base64
import json
import logging
import os

from pathlib import Path
from smtplib import SMTPException

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


logger = logging.getLogger(__name__)

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
]


class GmailEmailBackend(BaseEmailBackend):

    def get_credentials(self):

        # Renderでは、従来のSecret Filesを優先する。
        render_token_path = Path('/etc/secrets/token.json')

        if render_token_path.is_file():
            return Credentials.from_authorized_user_file(
                str(render_token_path),
                SCOPES,
            )

        # Belmoでは、環境変数から認証情報を読み込む。
        token_json = os.getenv(
            'GMAIL_TOKEN_JSON',
            '',
        ).strip()

        if token_json:
            token_info = json.loads(token_json)

            return Credentials.from_authorized_user_info(
                token_info,
                SCOPES,
            )

        # 自分のPCでは、manage.pyと同じ場所を使う。
        local_token_path = (
            settings.BASE_DIR / 'token.json'
        )

        return Credentials.from_authorized_user_file(
            str(local_token_path),
            SCOPES,
        )

    def send_messages(self, email_messages):

        messages = [
            message
            for message in (email_messages or [])
            if message.recipients()
        ]

        if not messages:
            return 0

        sent_count = 0

        try:
            if not getattr(settings, 'GMAIL_FROM_EMAIL', ''):
                raise ValueError(
                    'GMAIL_FROM_EMAIL is missing'
                )

            credentials = self.get_credentials()

            # アクセストークンが無効なら更新する。
            if not credentials.valid:
                if not credentials.refresh_token:
                    raise ValueError(
                        'refresh_token is missing'
                    )

                credentials.refresh(Request())

            with build(
                'gmail',
                'v1',
                credentials=credentials,
                cache_discovery=False,
            ) as service:

                for message in messages:
                    encoded_message = (
                        base64.urlsafe_b64encode(
                            message.message().as_bytes()
                        ).decode('ascii')
                    )

                    service.users().messages().send(
                        userId='me',
                        body={
                            'raw': encoded_message,
                        },
                    ).execute()

                    sent_count += 1

        except Exception as exc:
            # 認証情報やリセットURLはログへ出さない。
            status = getattr(
                getattr(exc, 'resp', None),
                'status',
                '-',
            )

            logger.error(
                'Gmail API send failed: %s; HTTP status=%s',
                type(exc).__name__,
                status,
            )

            if not self.fail_silently:
                # 今のviews.pyで受け取れる例外にする。
                raise SMTPException(
                    'Gmail APIでメールを送信できませんでした。'
                ) from None

        return sent_count