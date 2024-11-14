from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser
from django.dispatch import Signal
from .tasks import send_activation_email, send_password_reset_email
import django_rq



@receiver(post_save, sender=CustomUser)
def handle_send_activation_email(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        django_rq.enqueue(send_activation_email, instance)
         


password_reset_signal = Signal()
@receiver(password_reset_signal)    
def handle_send_password_reset_email(sender, user, **kwargs):
    django_rq.enqueue(send_password_reset_email, user)