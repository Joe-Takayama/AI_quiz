from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


BASE_DIR = Path(__file__).resolve().parent

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
]


def main():

    credentials_path = BASE_DIR / 'credentials.json'
    token_path = BASE_DIR / 'token.json'

    if not credentials_path.is_file():

        raise FileNotFoundError(
            'gmail_auth.pyと同じ場所に'
            'credentials.jsonを置いてください。'
        )

    flow = InstalledAppFlow.from_client_secrets_file(
        str(credentials_path),
        SCOPES,
    )

    credentials = flow.run_local_server(
        port=0,
        access_type='offline',
        prompt='consent',
    )

    if not credentials.refresh_token:

        raise RuntimeError(
            '更新用トークンを取得できませんでした。'
            'Googleの認証画面でメール送信を許可してください。'
        )

    # 更新用トークンが使えることを確認する。
    credentials.refresh(Request())

    # 認証に成功してから保存する。
    token_path.write_text(
        credentials.to_json(),
        encoding='utf-8',
    )

    print('Gmailの再認証が完了しました。')
    print('新しいtoken.jsonを作成しました。')


if __name__ == '__main__':
    main()