from .models import StreamLineSubscription
from django.utils import timezone
from rest_framework import status
import sendgrid
from sendgrid.helpers.mail import Mail
from .models import *

def store_temp_subs(user_sub):
    temp_subs = {}
    temp_subs['Basic'] = user_sub.Basic
    temp_subs['Basic_Expiration'] = user_sub.Basic_Expiration
    temp_subs['Premium'] = user_sub.Premium
    temp_subs['Premium_Expiration'] = user_sub.Premium_Expiration
    return temp_subs

def store_temp_data(user_data):
    temp_data = {}
    temp_data["budget"] = user_data.budget
    temp_data["bundle"] = user_data.bundle
    temp_data["media"] = user_data.media
    return temp_data

    
def checkSubscriptionStatus(user):
    sl_subscription = StreamLineSubscription.objects.get(user = user)

    # Check if subscription basic expiration date was before current time)
    if sl_subscription.Basic_Expiration is not None and sl_subscription.Basic_Expiration < timezone.now():
        sl_subscription.Basic = False
        sl_subscription.Basic_Expiration = None
        sl_subscription.save()
        # Check if subscription premium expiration date was before current time)
    if sl_subscription.Premium_Expiration is not None and sl_subscription.Premium_Expiration < timezone.now():
        sl_subscription.Premium = False
        sl_subscription.Premium_Expiration = None
        sl_subscription.save()
    if sl_subscription is None or (sl_subscription.Basic == False and sl_subscription.Premium == False):
        return False
    return True


# Action code 1: Default, keep/renew subscription
# Action code 2: Cancel subscription
# Action code 3: Swap subscription

def handleBasicAction(user_email, subscription, code):
    if code == 1:
        ## Send them an email saying their subscription will renew on x date
        ## Update subscription object with new expiration date
        template_id = "d-65eff9edfd4f47e493b649f54bb336f6"
        message = Mail(
        from_email='ekj0512@gmail.com',
        to_emails=user_email,
        )
        message.template_id = template_id
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
    elif code == 2:
        cur_subscription = ThirdPartySubscription.objects.get(user = user_email, subscription_name = subscription["name"])
        cur_subscription.end_date += timezone.timedelta(days=30)
        cur_subscription.save()
        ## Send them an email saying they need to cancel their subscription by x date
        ## Configure a webhook (in a bit) to send emails at 4 days and 1 day before expiration
        ## Update subscription object with cancellation and num_cancellations
        pass
    elif code == 3:
        ## Idk if we actually want to allow this for basic subscribers
        pass
    else:
        return status.HTTP_400_BAD_REQUEST

def handlePremiumAction(user, subscription, code):
    if code == 1:
        ## Send them an email saying their subscription will renew on x date
        ## Update subscription object with new expiration date
        ## Don't actually have to do anything else
        pass
    elif code == 2:
        ## Send them an email saying that we will cancel their subscription by x date (provided that they are within the timeframe)
        ## Try and find a way to cancel their subscription
        ## If we can't, send them an email saying that we couldn't cancel their subscription, and that they will have to do it manually (but this is a sep thing)
        ## Update subscription object with cancellation and num_cancellations
        ## Send a message to Dunny and Eliot to tell them that user x needs their subscription cancelled
        pass
    elif code == 3:
        ## Complicated shit
        pass
    else:
        return status.HTTP_400_BAD_REQUEST
