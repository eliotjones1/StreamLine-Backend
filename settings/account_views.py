from django.contrib.sessions.models import Session
from fuzzywuzzy import process
from rest_framework.decorators import api_view
from webhooks.models import UserStripePayment, UserStripeCustomer, UserPaymentInfo
from api.functions import *
from api.views import isSessionActive
from .functions import *
from .serializers import SubscriptionSerializer

## GOAL: Personalize our recommendations not only for TV and Movies but also for Streaming Services
## HOW TO DO IT: Beginning of user account subscription, ask them what kind of bundle they want, can either be
## One, where we recommend one service each month within budget, StreamLine, where we maximize their watchlist and minimize budget,
## and Max, where we get everything on watchlist while minimizing cost but without the budget constraint. 
## Can take into account what we would recommend to them, as well as their watchlist, their streaming service history, and budget, 
## and give them a detailed overview each month. Will track subscriptions over time, to see what they like and what they don't like,
## and will weight stuff they do like higher (maybe they like Netflix originals a lot so we weight Netflix higher). 


## New Subscriber Flow:
## 1. User signs up for StreamLine account
## 2. If user isn't subscribed, we don't take down any of their information
## 3. When user subscribes, we prompt them to input their watchlist, and what they are currently subscribed to. 
## These will get saved to UserData. From what they are currently subscribed to, we will get their monthly budget.
## 4. 


## Person goes to their dashboard
# They add a subscription, which becomes immeidately active
# They decide to cancel, renew, or swap a subscription. When this happens, if they cancel, just use the removeSubscription function.
# If they renew, make a new function to update the date, or say that the date will be updated on the next billing cycle.
# If they swap, make a new function to swap the subscription. This one will need more information. 


class AvailSubs(generics.ListAPIView):
    def get(self, request):

        search_query = request.query_params.get('search', None)
        if search_query is None:
            return Response({'error': 'Missing search query'}, status=status.HTTP_400_BAD_REQUEST)
        
        service_name = search_query
        df = pd.read_csv('api/random/pricing - Sheet2-3.csv')
        avail_services = df["Name"].tolist()

        # return four closest matching services
        results = process.extract(service_name, avail_services, limit=4)
        closest_strings = [result[0] for result in results]
        # return the four closest matching services
        return Response({'results': closest_strings}, status=status.HTTP_200_OK)
    

@api_view(['POST'])
def createSubscription(request):
    sessionid = request.COOKIES.get('sessionid')
    # print(sessionid)
    # Check if session is active
    if isSessionActive(sessionid) == False:
        return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
    # Needs to be exact string
    user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
    if user_email is None:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    subscription_info = request.data['body']
    print(subscription_info)
    # import dataframe from api/random/serviceImages.csv
    df = pd.read_csv('api/random/serviceImages.csv')
    # find image that corresponds to subscription_info['name']
    image_path = df.loc[df['service_name'] == subscription_info['Name']]['logo_path'].values[0]
    user = CustomUser.objects.get(email=user_email)
    this_subscription = ThirdPartySubscription.objects.create(user=user, subscription_name=subscription_info['Name'], end_date=subscription_info['End_Date'], num_months=1, num_cancellations=0, subscription_price=subscription_info['Price'], subscription_image_path=image_path, subscription_version=subscription_info['Version'], subscription_status = "Pending")
    this_subscription.save()

    customer = UserStripeCustomer.objects.get(user = user)
    end_date_str = subscription_info['End_Date']
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    new_date = end_date - timedelta(days=30)

    new_date_str = new_date.strftime('%Y-%m-%d')
    new_payment = UserStripePayment.objects.create(user = user, stripe_customer_id = customer,
                                                   date_of_payment = new_date_str, payment_amount = subscription_info['Price'],
                                                   transaction = subscription_info['Name'], transaction_status = 'pending')
    new_payment.save()
    return Response(SubscriptionSerializer(this_subscription).data, status=status.HTTP_200_OK)
## Find a way to activate this subscription on a certain date.

@api_view(['POST'])
def removeSubscription(request):
    sessionid = request.COOKIES.get('sessionid')
    # print(sessionid)
    # Check if session is active
    if isSessionActive(sessionid) == False:
        return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
    # expects user_id at 0, subscription info (name, date, recurring) at 1
    user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
    if user_email is None:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    subscription_info = request.data
    print(subscription_info)
    user = CustomUser.objects.get(email=user_email)
    this_subscription = ThirdPartySubscription.objects.get(user=user, subscription_name=subscription_info['subscription_name'])
    this_subscription.subscription_next_action = "cancel"
    this_subscription.save()
    return Response(status=status.HTTP_200_OK)
## New: Set the next subscription action to be "cancel". Write a new background function that checks the next action and completes on termination. 

@api_view(['POST'])
def renewSubscription(request):
    sessionid = request.COOKIES.get('sessionid')
    # print(sessionid)
    # Check if session is active
    if isSessionActive(sessionid) == False:
        return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
    # expects user_id at 0, subscription info (name, date, recurring) at 1
    user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
    if user_email is None:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    subscription_info = request.data
    user = CustomUser.objects.get(email=user_email)
    this_subscription = ThirdPartySubscription.objects.get(user=user, subscription_name=subscription_info['subscription_name']) 
    this_subscription.subscription_next_action = "renew"
    this_subscription.save()
    return Response(status=status.HTTP_200_OK)


class getSubscriptions(generics.ListAPIView):
    def get(self, request):
        # NAME, LOGO, END DATE, PRICE
        sessionid = request.COOKIES.get('sessionid')
        # print(sessionid)
        # Check if session is active
        if isSessionActive(sessionid) == False:
            return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
        # expects user_id at 0, subscription info (name, date, recurring) at 1
        user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
        if user_email is None:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        user = CustomUser.objects.get(email=user_email)
        subscriptions = ThirdPartySubscription.objects.filter(user=user)
        out = []
        for subscription in subscriptions:
            if subscription.subscription_status != "Expired":
                out.append(SubscriptionSerializer(subscription).data)
        # order out by end date soonest to latest
        out = sorted(out, key=lambda k: k['end_date'])
        update_status(user_email, repeat=86400)
        return Response(out, status=status.HTTP_200_OK)

            
@api_view(['POST'])
def generateBundle(request):
    sessionid = request.COOKIES.get('sessionid')
    # print(sessionid)
    # Check if session is active
    if isSessionActive(sessionid) == False:
        return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
    # expects user_id at 0, subscription info (name, date, recurring) at 1
    user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
    if user_email is None:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)    
    user = CustomUser.objects.get(email=user_email)
    user_data = UserData.objects.get(user=user)
    cur_subs =  ThirdPartySubscription.objects.filter(user=user)

    # TODO: Get all subscriptions for the user and create bundle
    # Bundle requires Links, Title, Subheader, Images, Total_Cost, Streaming_Services, Movies_and_TV_Shows
    # How to do: get user watchlist, and rig the optimization function to only include items not on current subscriptions

    # Get all titles on watchlist, current subscriptions
    subscriptions = list(cur_subs.values_list('subscription_name', flat=True))

    list_data = []
    for item in user_data.media:
        temp_data = {}
        item_info = getData(item)
        if item['media_type'] == 'tv':
            temp_data['title'] = item_info['name']
            temp_data['release_data'] = item_info['first_air_date']
            temp_data['image'] = item_info['poster_path']
            temp_data['streaming_providers'] = item_info['streaming_providers']
            temp_data['media_type'] = item_info['media_type']
            list_data.append(temp_data)
        else:
            temp_data['title'] = item_info['title']
            temp_data['release_data'] = item_info['release_date']
            temp_data['image'] = item_info['poster_path']
            temp_data['streaming_providers'] = item_info['streaming_providers']
            temp_data['media_type'] = item_info['media_type']
            list_data.append(temp_data)
    providers, prices, services = modify_input(list_data)

    ## Run optimization, but only on items not on current subscriptions
    watchlist = list(providers.keys())
    if len(watchlist) == 0:
        return Response(["Not available"], status=status.HTTP_400_BAD_REQUEST)
    x = {m: cp.Variable(boolean=True) for m in watchlist}
    y = {s: cp.Variable(boolean=True) for s in services}
    objective = cp.Minimize(cp.sum(1 - cp.vstack([x[m] for m in watchlist])))

    constraints = []
    for m in providers:
        constraints += [x[m] <= cp.sum(cp.vstack([y[s] for s in providers[m]]))]
        for s in services:
            if s in providers[m]:
                constraints += [y[s] <= cp.sum(cp.vstack([x[m] for m in providers]))]
    for s in services:
        if s in subscriptions:
            constraints += [y[s] == 1]
        else:
            constraints += [y[s] == 0]
    problem = cp.Problem(objective, constraints)
    problem.solve()

    output = {}
    output["Title"] = "Personal Bundle"
    output["Subheader"] = "Just for you"
    output["Movies_and_TV_Shows"] = []
    output["Streaming_Services"] = []
    output["Total_Cost"] = 0

    output["Movies_and_TV_Shows"] = []
    output["Type"] = []
    for s in services:
        if y[s].value == 1:
            output["Streaming_Services"].append(s)
            output["Total_Cost"] += prices[s]

    for m in watchlist:
        if x[m].value == 1:
            output["Movies_and_TV_Shows"].append(m)

    for media in output["Movies_and_TV_Shows"]:
        for object in list_data:
            if media == object["title"]:
                output["Type"].append(object["media_type"])
    realOutput = getServiceImages(output)
    print(realOutput)
    user_data.bundle = [realOutput]
    user_data.budget = round(realOutput["Total_Cost"], 7)
    user_data.save()
    return Response(status=status.HTTP_200_OK)

class getMyUpcoming(generics.ListAPIView):
    def get(self, request):
        sessionid = request.COOKIES.get('sessionid')
        if isSessionActive(sessionid) == False:
            return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
        user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
        if user_email is None:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        user = CustomUser.objects.get(email=user_email)
        subscriptions = ThirdPartySubscription.objects.filter(user=user)
        subscriptions = list(subscriptions.values_list('subscription_name', flat=True))
        # Get subscription ids from subscription names
        df = pd.read_csv('api/random/serviceImages.csv')
        df = df[df['service_name'].isin(subscriptions)]
        subscription_ids = []
        for subscription in subscriptions:
            subscription_ids.append(str(df.loc[df['service_name'] == subscription]['id'].values[0]))

        release_year = datetime.now().year
        separator = "|"
        subscription_ids = separator.join(subscription_ids)
        # TV SHOWS
        url = "https://api.themoviedb.org/3/discover/tv?first_air_date_year=" + str(release_year) + "&include_adult=false&include_null_first_air_dates=false&language=en-US&page=1&sort_by=popularity.desc&watch_region=US&with_watch_providers=" + subscription_ids
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NWNkNTI3OWYxN2M2NTkzMTIzYzcyZDA0ZTBiZWRmYSIsInN1YiI6IjY0NDg4NTgzMmZkZWM2MDU3M2EwYjk3MCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.VXG36aVRaprnsBeXXhjGq6RmRRoPibEuGsjkgSB-Q-c"
        }
        response = requests.get(url, headers=headers)
        new_shows = response.json()['results']

        # MOVIES
        url = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&primary_release_year=" + str(release_year) + "&sort_by=popularity.desc&watch_region=US&with_watch_providers=" + subscription_ids
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NWNkNTI3OWYxN2M2NTkzMTIzYzcyZDA0ZTBiZWRmYSIsInN1YiI6IjY0NDg4NTgzMmZkZWM2MDU3M2EwYjk3MCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.VXG36aVRaprnsBeXXhjGq6RmRRoPibEuGsjkgSB-Q-c"
        }
        response = requests.get(url, headers=headers)
        new_movies = response.json()['results']

        # NEED TO FIND SHOWS BEING RELEASED THIS WEEK
        output = []
        for show in new_shows:
            # Check if it is released this week
            if show['first_air_date'] is not None and show['first_air_date'][:10] >= str(datetime.now().date()) and show['first_air_date'][:10] <= str(datetime.now().date() + timedelta(days=7)):
                # Check if it is on a subscription
                show['media_type'] = "tv"
                output.append(show)
        for movie in new_movies:
            # Check if it is released this week
            if movie['release_date'] is not None and movie['release_date'][:10] >= str(datetime.now().date()) and movie['release_date'][:10] <= str(datetime.now().date() + timedelta(days=7)):
                # Check if it is on a subscription
                movie['media_type'] = "movie"
                output.append(movie)
        return Response(output, status=status.HTTP_200_OK)
                

## For user-dash
# Need option to add a service: take top four recommended services (based on stuff in watchlist), or the ability to search and add a service
# If a user is a basic member:
###### Order services by expiring soonest to latest. If within 7 days of expiry, status = expiring. We send them emails on 7 days, 4 days, and 1 day, and if they remove
###### a service from their list, we send them a reminder email saying that they have to take this action. 
# If a user is a premium member
###### Still order services by expiry date. When a service is expiring, we give them options: they can keep it, they can cancel it, or they can switch to a new service.
###### All of this we should handle ourselves. When they click "actions", should give a pop up with three columnsL "delete", "keeo", and "switch", each with different kinds
###### of information that we are giving them. Send them emails as well, but we are responsible for handling everything. 

# Need a webhook that tracks the number of days left in a subscription to notify individuals and change tags. 

## UD #1: show potential services button
class recommendedServices(generics.ListAPIView):
    def get(self, request):
        sessionid = request.COOKIES.get('sessionid')
        if isSessionActive(sessionid) == False:
            return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
        user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
        if user_email is None:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        user = CustomUser.objects.get(email=user_email)
        # Assume bundles have already been generated
        bundle = UserData.objects.get(user=user).bundle[0]
        current_services = ThirdPartySubscription.objects.filter(user=user)
        current_services = list(current_services.values_list('subscription_name', flat=True))
        output = []
        service_df = pd.read_csv('api/random/pricing - Copy of Sheet1-2.csv')
        service_images = pd.read_csv('api/random/serviceImages.csv')
        for service in bundle["Streaming_Services"]:
            if service not in current_services:
                # find row in service_df that corresponds to service
                service_info = {}
                service_info["Name"] = service
                service_row = service_df.loc[service_df['Name'] == service]
                service_info["Link"] = service_row['Link'].values[0]
                service_info["Packages"] = []
                # loop over the 1-8th columns in the row (0 indexed)
                i = 1
                while i < 9:
                    if service_row.iloc[0][i] is not None:
                        if not pd.isna(service_row.iloc[0, i]) and not pd.isna(service_row.iloc[0, i+1]):
                            service_info["Packages"].append(
                                {
                                    "Version": service_row.iloc[0, i],
                                    "Price": service_row.iloc[0,i+1],
                                }
                                )
                    i += 2
                print(service_info)
                service_info["Image"] = service_images.loc[service_images['service_name'] == service]['logo_path'].values[0]
                print(service_info)
                output.append(service_info)
        return Response(output, status=status.HTTP_200_OK)
