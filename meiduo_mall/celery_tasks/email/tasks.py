from django.core.mail import send_mail
from django.conf import settings
from celery_tasks.main import celery_app


@celery_app.task(name='send_verify_mail')
def send_verify_email(to_email=None, subject=None, html_message=None):

    result = send_mail(subject,
             "",
             settings.EMAIL_FROM,
             [to_email],
              html_message=html_message
             )
    return result


