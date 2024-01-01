import requests
from .models import *
from api.views import isSessionActive
from authentication.models import CustomUser
from django.contrib.sessions.models import Session
from .functions import *
from settings.models import *

## Virtual Cable Box API Calls
# 1). For the Featured content, show the top trending show on each of their platforms
# 2). Have sections for every service they are subscribed to with:
#       a). Items from their watchlist
#       b). Trending content from that service
#       c). Upcoming content from that service
#       d). Space for recommendations but that can come later

####### HELPER FUNCTIONS ########

def find_trending(services):
    base_url = 'https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc&watch_region=US&with_watch_providers='
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NWNkNTI3OWYxN2M2NTkzMTIzYzcyZDA0ZTBiZWRmYSIsInN1YiI6IjY0NDg4NTgzMmZkZWM2MDU3M2EwYjk3MCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.VXG36aVRaprnsBeXXhjGq6RmRRoPibEuGsjkgSB-Q-c"
    }
    temp = []
    for id in services:
        response = requests.get(base_url + str(id), headers = headers)
        if response.status_code != 200:
            continue  # Skip to next page on error

        for item in response.json().get('results', []):
            temp.append(getData(item))
            break
    return temp


##################################

class FeaturedContent(generics.ListAPIView):
    # Would love to find a way to get this specific to their services but might not be feasible
    def get(self, request):
        sessionid = request.COOKIES.get('sessionid')
        if isSessionActive(sessionid) == False:
            return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
        user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
        if user_email is None:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        user = CustomUser.objects.get(email = user_email)
        subscriptions = ThirdPartySubscription.objects.filter(user=user)

        subscriptions = [subscription['subscription_name'] for subscription in subscriptions if subscription.subscription_status != "Expired"]
        # Get subscription ids from subscription names
        df = pd.read_csv('api/random/serviceImages.csv')
        df = df[df['service_name'].isin(subscriptions)]
        subscription_ids = []
        for subscription in subscriptions:
            subscription_ids.append(str(df.loc[df['service_name'] == subscription]['id'].values[0]))

        trending = find_trending(subscription_ids)
        return Response(trending, status=status.HTTP_200_OK)