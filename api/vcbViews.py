import requests
from .models import *
from api.views import isSessionActive
from authentication.models import CustomUser
from django.contrib.sessions.models import Session
from .functions import *
from settings.models import *
from datetime import datetime


## Virtual Cable Box API Calls
# 1). For the Featured content, show the top trending show on each of their platforms
# 2). Have sections for every service they are subscribed to with:
#       a). Items from their watchlist
#       b). Trending content from that service
#       c). Upcoming content from that service
#       d). Space for recommendations but that can come later

####### HELPER FUNCTIONS ########

def find_trending(services):
    ###### NOTE ########
    ###### PRIMARY RELEASE YEAR LOCKED TO 2023 CHANGE AT SOME POINT #########
    movie_url = 'https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc&watch_region=US&with_watch_providers='
    show_url = 'https://api.themoviedb.org/3/discover/tv?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc&watch_region=US&with_watch_providers='
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NWNkNTI3OWYxN2M2NTkzMTIzYzcyZDA0ZTBiZWRmYSIsInN1YiI6IjY0NDg4NTgzMmZkZWM2MDU3M2EwYjk3MCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.VXG36aVRaprnsBeXXhjGq6RmRRoPibEuGsjkgSB-Q-c"
    }
    temp = []
    for id in services:
        movie_response = requests.get(movie_url + str(id), headers = headers)
        if movie_response.status_code != 200:
            continue  # Skip to next page on error

        for item in movie_response.json().get('results', []):
            item['media_type'] = 'movie'
            temp.append(getData(item))
            break

        tv_response = requests.get(show_url + str(id), headers = headers)
        if tv_response.status_code != 200:
            continue
        for item2 in tv_response.json().get('results', []):
            item2['media_type'] = 'tv'
            temp.append(getData(item2))
            break
            
    return temp

def trending(subscription_id):
    movie_url = 'https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc&watch_region=US&with_watch_providers='
    show_url = 'https://api.themoviedb.org/3/discover/tv?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc&watch_region=US&with_watch_providers='
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NWNkNTI3OWYxN2M2NTkzMTIzYzcyZDA0ZTBiZWRmYSIsInN1YiI6IjY0NDg4NTgzMmZkZWM2MDU3M2EwYjk3MCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.VXG36aVRaprnsBeXXhjGq6RmRRoPibEuGsjkgSB-Q-c"
    }
    out = []
    movie_response = requests.get(movie_url + str(subscription_id), headers = headers)
    for item in movie_response.json().get('results', []):
        item['media_type'] = 'movie'
        out.append(getData(item))
        if len(out) == 5:
            break
    tv_response = requests.get(show_url + str(subscription_id), headers = headers)
    for item2 in tv_response.json().get('results', []):
        item2['media_type'] = 'tv'
        out.append(getData(item2))
        if len(out) == 10:
            break
    return out

def upcoming(subscription_id):
    format_str = "%Y-%m-%d"
    tv_url = "https://api.themoviedb.org/3/discover/tv?first_air_date.gte=" + str(datetime.now().date()) + "&include_adult=false&include_null_first_air_dates=false&language=en-US&page=1&sort_by=popularity.desc&watch_region=US&with_watch_providers="
    movie_url = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&primary_release_date.gte=" + str(datetime.now().date()) + "&sort_by=popularity.desc&watch_region=US&with_watch_providers="
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NWNkNTI3OWYxN2M2NTkzMTIzYzcyZDA0ZTBiZWRmYSIsInN1YiI6IjY0NDg4NTgzMmZkZWM2MDU3M2EwYjk3MCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.VXG36aVRaprnsBeXXhjGq6RmRRoPibEuGsjkgSB-Q-c"
    }

    out = []
    movie_response = requests.get(movie_url + str(subscription_id), headers=headers)
    for movie in movie_response.json().get('results', []):
        if movie['release_date'] is not None and datetime.strptime(movie['release_date'][:10], format_str).date() >= datetime.now().date():
            movie['media_type'] = 'movie'
            out.append(getData(movie))

    tv_response = requests.get(tv_url + str(subscription_id), headers=headers)
    for tv in tv_response.json().get('results', []):
        if tv['first_air_date'] is not None and datetime.strptime(tv['first_air_date'][:10], format_str).date() >= datetime.now().date():
            tv['media_type'] = 'tv'
            out.append(getData(tv))
    return out

def getWatchlist(media):
    out = []
    for item in media:
        out.append(getData(item))
    return out


def getServiceContent(subscription_id, subscription_name, watchlist):
    return_dict = {}
    # Trending on
    return_dict["Trending"] = trending(subscription_id)

    # Upcoming
    return_dict["Upcoming"] = upcoming(subscription_id)

    # In watchlist
    return_dict["In_Watchlist"] = []
    temp = [item for item in watchlist if item['streaming_providers']]
    for item in temp:
        streaming_providers = set(item['streaming_providers']['free'] + item['streaming_providers']['ads'] + item['streaming_providers']['flatrate'])
        if subscription_name in streaming_providers:
            return_dict["In_Watchlist"].append(item)
    return return_dict

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

        subscriptions = [subscription.subscription_name for subscription in subscriptions if subscription.subscription_status != "Expired"]
        # Get subscription ids from subscription names
        df = pd.read_csv('api/random/serviceImages.csv')
        df = df[df['service_name'].isin(subscriptions)]
        subscription_ids = []
        for subscription in subscriptions:
            subscription_ids.append(str(df.loc[df['service_name'] == subscription]['id'].values[0]))

        trending = find_trending(subscription_ids)
        return Response(trending, status=status.HTTP_200_OK)

class ServiceContent(generics.ListAPIView):
    def get(self, request):
        sessionid = request.COOKIES.get('sessionid')
        if isSessionActive(sessionid) == False:
            return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
        user_email = Session.objects.get(session_key=sessionid).get_decoded()['user_email']
        if user_email is None:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        user = CustomUser.objects.get(email = user_email)
        user_data = UserData.objects.get(user_id = user)
        subscriptions = ThirdPartySubscription.objects.filter(user=user)

        subscriptions = [subscription.subscription_name for subscription in subscriptions if subscription.subscription_status != "Expired"]
        # Get subscription ids from subscription names
        df = pd.read_csv('api/random/serviceImages.csv')
        service_info = pd.read_csv('api/random/pricing - Copy of Sheet1-2.csv')

        df = df[df['service_name'].isin(subscriptions)]
        subscription_ids = []
        for subscription in subscriptions:
            subscription_ids.append(str(df.loc[df['service_name'] == subscription]['id'].values[0]))

        media_list = user_data.media
        watchlist = getWatchlist(media_list)
        out = {}
        for index, id in enumerate(subscription_ids):
            out[subscriptions[index]] = {}
            out[subscriptions[index]]['content'] = getServiceContent(id, subscriptions[index], watchlist)
            link = service_info.loc[service_info['Name'] == subscriptions[index]]['Link'].values[0]
            image = df.loc[df['service_name'] == subscriptions[index]]['logo_path'].values[0]
            out[subscriptions[index]]['info'] = {'link':link, 'image':image}

        return Response(out, status = status.HTTP_200_OK)


