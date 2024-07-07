from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
# Create your models here.
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
import sendgrid
from sendgrid.helpers.mail import Mail
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
import json



class CustomUser(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    first_name = models.CharField('First Name', max_length=255, blank=True,
                                  null=False)
    last_name = models.CharField('Last Name', max_length=255, blank=True,
                                 null=False)
    REQUIRED_FIELDS = ['first_name', 'last_name']
    USERNAME_FIELD = 'email'

    def __str__(self):
        return f"{self.email} - {self.first_name} {self.last_name}"
    def to_json(self):
        user_data = {
            'id': self.id,
        }
        return json.dumps(user_data)
    
@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    token = reset_password_token.key
    reset_password_url = 'http://localhost:5173/secure-reset?' + token
    expiry_time = timezone.now() + timedelta(minutes=15)
    template_id = "d-467cfdba14174276864542097b246c07"
    # email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'), reset_password_token.key)
    email_plaintext_message = f"Click the link below to reset your password: \n\n{reset_password_url}"
    message = Mail(
        from_email='ekj0512@gmail.com',
        to_emails=[reset_password_token.user.email],
        subject = "StreamLine Password Reset",
        plain_text_content=email_plaintext_message
    )
    message.template_id = template_id
    reset_password_token.expires = expiry_time
    reset_password_token.save()
    try:
        sg = sendgrid.SendGridAPIClient(api_key='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')
        response = sg.send(message)
        if response.status_code == 202:
            pass
        else:
            return Response({})
    except Exception as e:
        pass
    




