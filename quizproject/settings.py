import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


# ====================================
# 基本設定
# ====================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

IS_RENDER = os.getenv('RENDER', '').lower() == 'true'


# ====================================
# シークレットキー
# ====================================

SECRET_KEY = os.getenv('SECRET_KEY')

if not SECRET_KEY:

    raise ImproperlyConfigured(
        '.envまたはRenderの環境変数に'
        'SECRET_KEYを設定してください。'
    )


# ====================================
# デバッグ
# ローカルでは有効、Renderでは無効
# ====================================

DEBUG = not IS_RENDER


ALLOWED_HOSTS = [
    '.onrender.com',
    'localhost',
    '127.0.0.1',
]


# ====================================
# アプリケーション
# ====================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'quizapp.apps.QuizappConfig',
    'accounts.apps.AccountsConfig',
]


# ====================================
# ミドルウェア
# ====================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'quizproject.urls'


# ====================================
# テンプレート
# ====================================

TEMPLATES = [
    {
        'BACKEND': (
            'django.template.backends.django.DjangoTemplates'
        ),

        'DIRS': [
            BASE_DIR / 'templates',
        ],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'quizproject.wsgi.application'


# ====================================
# データベース
# 前回と同じくDATABASE_URLで切り替える
# ====================================

DATABASE_URL = os.getenv('DATABASE_URL', '').strip()

if DATABASE_URL:

    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        ),
    }

elif IS_RENDER:

    raise ImproperlyConfigured(
        'Renderの環境変数に'
        'SupabaseのDATABASE_URLを設定してください。'
    )

else:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        },
    }


# ====================================
# パスワード検証
# ====================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator'
        ),
    },
]


# ====================================
# 言語・タイムゾーン
# ====================================

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# ====================================
# CSS・JavaScript・画像
# ====================================

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'


# ====================================
# ログイン・ログアウト
# ====================================

LOGIN_URL = 'accounts:login'

LOGIN_REDIRECT_URL = 'quizapp:index'

LOGOUT_REDIRECT_URL = 'quizapp:index'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ====================================
# メール
# Gmail APIの接続は別の工程で設定する
# ====================================

EMAIL_BACKEND = (
    'django.core.mail.backends.console.EmailBackend'
)

DEFAULT_FROM_EMAIL = 'DataQuiz AI <noreply@example.com>'

PASSWORD_RESET_TIMEOUT = 3600


# ====================================
# Gemini API
# ====================================

GEMINI_API_KEY = os.getenv(
    'GEMINI_API_KEY',
    '',
)

GEMINI_MODEL = os.getenv(
    'GEMINI_MODEL',
    'gemini-3.5-flash-lite',
)

GMAIL_FROM_EMAIL = os.getenv(
    "GMAIL_FROM_EMAIL"
)


# ====================================
# RenderのHTTPS設定
# ====================================

if IS_RENDER:

    SECURE_PROXY_SSL_HEADER = (
        'HTTP_X_FORWARDED_PROTO',
        'https',
    )

    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True