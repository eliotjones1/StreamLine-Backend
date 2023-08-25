from .models import StreamLineSubscription
from django.utils import timezone

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


