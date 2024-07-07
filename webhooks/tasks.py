from background_task import background
from authentication.models import CustomUser
from settings.models import ThirdPartySubscription
from datetime import datetime, timedelta
import sendgrid
from sendgrid.helpers.mail import Mail
from rest_framework import status
from .models import UserStripePayment, UserStripeCustomer


@background(schedule=60)
def update_status(user_email):
    user = CustomUser.objects.get(email=user_email)
    user_subscriptions = ThirdPartySubscription.objects.filter(user=user)

    for subscription in user_subscriptions:
        date = subscription.end_date
        status = subscription.subscription_status
        if status == "Active":
            if date < datetime.now() + timedelta(days=7):
                subscription.subscription_status = 'Expiring'
                subscription.save()
        if status == "Expiring":
            if date < datetime.now():
                if subscription.subscription_next_action == "cancel":
                    subscription.subscription_status = 'Expired'
                    subscription.save()
                elif subscription.subscription_next_action == "renew":
                    subscription.subscription_status = 'Active'

                    customer = UserStripeCustomer.objects.get(user = user)

                    new_payment = UserStripePayment.objects.create(user = user, stripe_customer_id = customer.stripe_customer_id,
                                                                   date_of_payment = subscription.end_date, payment_amount = subscription.subscription_price,
                                                                   transaction = subscription.subscription_name, transaction_status = ['paid'])
                    new_payment.save()
                    
                    subscription.end_date += timedelta(days=30)
                    subscription.save()


                else:
                    pass
        if status == "Pending":
            if date > datetime.now().date():
                subscription.subscription_status = 'Active'
                subscription.save()

                sub_payment = UserStripePayment.objects.get(user = user, transaction = subscription.subscription_name)
                sub_payment.transaction_status = 'paid'
                sub_payment.save()




@background(schedule=60)
def send_cancellation_reminders(user_email, subscription):
    date = subscription.end_date
    name = subscription.subscription_name
    # template_id = ## Cancellation id
    ## Need to add date and name
    message = Mail(
    from_email='ekj0512@gmail.com',
    to_emails=user_email,
    )
    # message.template_id = template_id
    try:
        sg = sendgrid.SendGridAPIClient(api_key='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')  # Replace with your SendGrid API key
        response = sg.send(message)
        print(response)
        if response.status_code == 202:
            pass
        else:
            return status.HTTP_400_BAD_REQUEST
    except Exception as e:
        print(str(e))
        pass

### FIGURE STUFF OUT FOR BASIC SUBSCRIPTION FIRST
### ADD PAYMENTS BASED ON THIRD PARTY SUBSCRIPTIONS