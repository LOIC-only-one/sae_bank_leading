from django.core.mail import send_mail
from django.conf import settings

def send_validation_email(user_email, message):
    subject = "Validation de votre compte"
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False
    )
