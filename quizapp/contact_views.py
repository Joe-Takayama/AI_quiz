import logging
import os

from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.shortcuts import render, redirect
from django.views import View

from .contact_forms import ContactForm


logger = logging.getLogger(__name__)


class ContactView(View):

    # ====================================
    # お問い合わせ画面
    # ====================================

    def get(self, request):

        initial = {}

        if request.user.is_authenticated:

            initial = {
                'name': (
                    request.user.get_full_name()
                    or request.user.get_username()
                ),

                'email': request.user.email,
            }

        form = ContactForm(initial=initial)

        return self.render_page(
            request,
            form,
        )

    # ====================================
    # お問い合わせをメール送信
    # ====================================

    def post(self, request):

        form = ContactForm(request.POST)

        if not form.is_valid():

            return self.render_page(
                request,
                form,
            )

        recipient = os.getenv(
            'CONTACT_TO_EMAIL',
            '',
        ).strip()

        try:

            validate_email(recipient)

        except ValidationError:

            logger.error(
                'CONTACT_TO_EMAIL is missing or invalid'
            )

            form.add_error(
                None,
                '現在お問い合わせを送信できません。'
                '時間をおいて再度お試しください。',
            )

            return self.render_page(
                request,
                form,
            )

        data = form.cleaned_data

        body = (
            'DataQuiz AIにお問い合わせが届きました。\n\n'
            '━━━━━━━━━━━━━━━━━━━━\n'
            f"お名前：{data['name']}\n"
            f"返信先：{data['email']}\n"
            f"件名：{data['subject']}\n"
            '━━━━━━━━━━━━━━━━━━━━\n\n'
            '【お問い合わせ内容】\n\n'
            f"{data['message']}\n\n"
            '━━━━━━━━━━━━━━━━━━━━\n'
            '返信する場合は、メールの返信機能を使用してください。\n'
        )

        email = EmailMessage(
            subject=(
                '[DataQuiz AI お問い合わせ] '
                f"{data['subject']}"
            ),

            body=body,

            # 既存のGmail送信用アドレスを使用する。
            from_email=settings.DEFAULT_FROM_EMAIL,

            # 管理者の受信先。
            to=[recipient],

            # メールの「返信」で問い合わせ者へ返信できる。
            reply_to=[data['email']],
        )

        try:

            sent_count = email.send(
                fail_silently=False,
            )

            if sent_count != 1:

                raise SMTPException(
                    'メールを送信できませんでした。'
                )

        except (SMTPException, OSError, ValueError) as exc:

            # メール本文や個人情報はログに出さない。
            logger.warning(
                'Contact email failed: %s',
                type(exc).__name__,
            )

            form.add_error(
                None,
                'メールを送信できませんでした。'
                '時間をおいて再度お試しください。',
            )

            return self.render_page(
                request,
                form,
            )

        messages.success(
            request,
            'お問い合わせを送信しました。',
        )

        return redirect(
            'quizapp:contact'
        )

    # ====================================
    # 画面表示
    # ====================================

    def render_page(self, request, form):

        return render(
            request,
            'quizapp/contact.html',
            {
                'form': form,
            },
        )