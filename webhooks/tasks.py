from background_task import background
from authentication.models import CustomUser
from settings.models import ThirdPartySubscription
from datetime import datetime, timedelta
import sendgrid
from sendgrid.helpers.mail import Mail
from rest_framework import status



@background(schedule=60)
def update_status(user_email):
    user = CustomUser.objects.get(email=user_email)
    user_subscriptions = ThirdPartySubscription.objects.filter(user=user)

    for subscription in user_subscriptions:
        date = subscription.end_date
        status = subscription.subscription_status
        if status == "Active":
            if date < datetime.now() + timedelta(days=7):
                subscription.status = 'Expiring'
                subscription.save()
        if status == "Expiring":
            if date < datetime.now():
                if subscription.subscription_next_action == "cancel":
                    subscription.subscription_status = 'Expired'
                    subscription.save()
                elif subscription.subscription_next_action == "renew":
                    subscription.subscription_status = 'Active'
                    subscription.end_date += timedelta(days=30)
                    subscription.save()
                else:
                    pass
        if status == "Pending":
            if date < datetime.now().date():
                subscription.status = 'Active'
                subscription.save()


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

