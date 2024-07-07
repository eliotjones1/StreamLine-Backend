from django.db import models
from authentication.models import CustomUser
# Create your models here.

class UserStripeCustomer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255)

class UserPaymentInfo(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    stripe_customer_id = models.OneToOneField(UserStripeCustomer, on_delete=models.CASCADE)
    stripe_payment_info = models.CharField(max_length=1000)


class UserStripePayment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    stripe_customer_id = models.ForeignKey(UserStripeCustomer, on_delete=models.CASCADE)
    date_of_payment = models.DateTimeField(auto_now_add=True)
    payment_amount = models.FloatField()
    transaction = models.CharField(max_length=255)
    transaction_status = models.CharField(max_length=255)






