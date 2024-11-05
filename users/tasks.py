import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator



def send_activation_email(instance):
    # generate Token and UID
    token = default_token_generator.make_token(instance)
    uid = urlsafe_base64_encode(force_bytes(instance.pk))

    # generate activation url
    activation_url = os.getenv('FRONTEND_URL')
    activation_url_full = f"{activation_url}verify-account/?uid={uid}&token={token}"

    # load email template
    html_content = render_to_string('confirm_email.html', {
        'user': instance,
        'activation_url': activation_url_full,
    })
    text_content = strip_tags(html_content)

    # send email
    email = EmailMultiAlternatives(
        subject='Confirm your email',
        body=text_content,
        from_email='mail@ricardogeada.com',
        to=[instance.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    
    

def send_password_reset_email(user):
    # generate Token and UID
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    # generate reset url
    reset_url = os.getenv('FRONTEND_URL')
    reset_url_full = f"{reset_url}reset-password/?uid={uid}&token={token}"

    # load email template
    html_content = render_to_string('password_reset_email.html', {
        'user': user,
        'reset_url': reset_url_full,
    })
    text_content = strip_tags(html_content)

    # send email
    email = EmailMultiAlternatives(
        subject='Reset your password',
        body=text_content,
        from_email='mail@ricardogeada.com',
        to=[user.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()