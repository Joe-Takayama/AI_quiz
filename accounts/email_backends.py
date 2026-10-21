import base64
import logging

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

            # RenderではSecret Filesを使う。
            token_path = Path('/etc/secrets/token.json')

            # 自分のPCではmanage.pyと同じ場所を使う。
            if not token_path.is_file():

                token_path = (
                    settings.BASE_DIR / 'token.json'
                )

            credentials = (
                Credentials.from_authorized_user_file(
                    str(token_path),
                    SCOPES,
                )
            )

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

                # 今のviews.pyの例外処理で受け取れる形にする。
                raise SMTPException(
                    'Gmail APIでメールを送信できませんでした。'
                ) from None

        return sent_count