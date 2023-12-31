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
    base_url = "https://api.themoviedb.org/3"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NWNkNTI3OWYxN2M2NTkzMTIzYzcyZDA0ZTBiZWRmYSIsInN1YiI6IjY0NDg4NTgzMmZkZWM2MDU3M2EwYjk3MCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.VXG36aVRaprnsBeXXhjGq6RmRRoPibEuGsjkgSB-Q-c"
    }
    trending = "/trending/all/week"
    provider_url = "/watch/providers"
    results = []
    temp = []
    for page in range(1):  # Iterate over 10 pages
        response = requests.get(f"{base_url}{trending}?page={page}", headers=headers)
        print(response)
        if response.status_code != 200:
            continue  # Skip to next page on error

        for item in response.json().get('results', []):
            media_type = item['media_type']
            media_id = item['id']
            providers_response = requests.get(f"{base_url}/{media_type}/{media_id}{provider_url}", headers=headers)
            print(providers_response)
            if page == 1:
                temp.append(item)
            if providers_response.status_code == 200:
                providers_data = providers_response.json().get('results', {})
                for service in services:
                    if service in providers_data:
                        results.append(item)
                        services.remove(service)
                        break
    print(results)
    print(temp[:3])
    if not results:
        return temp[:3]
    else:
        return results


##################################

class FeaturedContent(generics.ListAPIView):
    def get(self, request):
        sessionid = request.COOKIES.get('sessionid')
        if isSessionActive(sessionid) == False:
            return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
        user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
        if user_email is None:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        user = CustomUser.objects.get(email = user_email)
        subscriptions = ThirdPartySubscription.objects.filter(user=user)

        subscriptions = [subscription for subscription in subscriptions if subscription.subscription_status != "Expired"]
        out = find_trending(subscriptions)
        return Response(out, status=status.HTTP_200_OK)