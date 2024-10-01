from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def send_activation_email(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        # generate Token and UID
        token = default_token_generator.make_token(instance)
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        
        # generate activation url
        activation_url = reverse('activate_account', kwargs={'uidb64': uid, 'token': token})
        activation_url_full = f"http://127.0.0.1:8000//{activation_url}"
        
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
        