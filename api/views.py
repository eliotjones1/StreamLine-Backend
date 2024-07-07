# Create your views here.
from datetime import datetime

from django.contrib.sessions.models import Session
from django.utils import timezone
from fuzzywuzzy import fuzz
from rest_framework.decorators import api_view

from authentication.models import CustomUser
from settings.models import UserData
from settings.serializers import UserDataSerializer
from .functions import *
from .models import StaffPick

# Create your views here.
format_str = "%Y-%m-%d"


class returnAll(generics.ListAPIView):
    def get(self, request):
        search_query = request.query_params.get('search', None)
        if search_query is None:
            return Response({'error': 'Missing search query'}, status=status.HTTP_400_BAD_REQUEST)
        title = search_query
        
        # Get Movies

        url = "https://api.themoviedb.org/3/search/multi?query=" + title + "&include_adult=false&language=en-US&page=1"

        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NWNkNTI3OWYxN2M2NTkzMTIzYzcyZDA0ZTBiZWRmYSIsInN1YiI6IjY0NDg4NTgzMmZkZWM2MDU3M2EwYjk3MCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.VXG36aVRaprnsBeXXhjGq6RmRRoPibEuGsjkgSB-Q-c"
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None
        data = response.json()['results']
        return Response(data, status=status.HTTP_200_OK)


def isSessionActive(sessionid):
    try:
        session = Session.objects.get(pk=sessionid)
    except:
        return False
    if session.expire_date > timezone.now():
        return True
    else:
        return False


@api_view(['POST'])
def saveBudget(request):
    # get sessionid from request cookie
    sessionid = request.COOKIES.get('sessionid')
    # Check if session is active
    if isSessionActive(sessionid) == False:
        return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)

    budget = request.data
    user_email = Session.objects.get(
        session_key=sessionid).get_decoded()['user_email']
    if user_email is None:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    user_exists = CustomUser.objects.get(email=user_email)
    current = UserData.objects.get(user_id=user_exists)
    current.budget = budget
    current.save()
    return Response({"Status": "OK"})

class checkInList(generics.ListAPIView):
    def get(self, request):
        sessionid = request.COOKIES.get('sessionid')
        # Check if session is active
        if isSessionActive(sessionid) == False:
            return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
        user_email = Session.objects.get(
            session_key=sessionid).get_decoded()['user_email']
        if user_email is None:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        id = str(request.query_params.get('id', None))
        media_type = request.query_params.get('media_type', None)
        user_exists = CustomUser.objects.get(email=user_email)
        current = UserData.objects.get(user_id=user_exists)
        cur_list = current.media

        ids = []
        types = []
        for elem in cur_list:
            ids.append(elem["id"])
            types.append(elem["media_type"])

        if id in ids:
            # find the index in cur_list[0]
            indecies = [index for index, item in enumerate(ids) if item == id]
            for index in indecies:
                if types[index] == media_type:
                    return Response({"Status": "true"}, status=status.HTTP_200_OK)
        else:
            return Response({"Status": "false"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def saveMedia(request):
    # get sessionid from request cookie
    sessionid = request.COOKIES.get('sessionid')
    # Check if session is active
    if isSessionActive(sessionid) == False:
        return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
    user_email = Session.objects.get(
        session_key=sessionid).get_decoded()['user_email']
    if user_email is None:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    # Expects a dict with "id" and "type" as keys
    object = request.data
    user_exists = CustomUser.objects.get(email=user_email)
    current = UserData.objects.get(user_id=user_exists)
    cur_list = current.media
    # Get all values corresponding to the "id" key in each dict:
    ids = []
    types = []
    for elem in cur_list:
        ids.append(elem["id"])
        types.append(elem["media_type"])
    if str(object["id"]) in ids:
        indecies = [index for index, item in enumerate(ids) if item == object["id"]]
        for index in indecies:
            if types[index] == object["media_type"]:
                return Response({"Status": "already in list"}, status=status.HTTP_400_BAD_REQUEST)
    cur_list.append({"id": str(object["id"]), "media_type": object["media_type"]})
    current.media = cur_list
    current.save()
    return Response({"Status": "OK"}, status=status.HTTP_200_OK)

@api_view(['POST'])
def clearMedia(request):
 # get sessionid from request cookie
    sessionid = request.COOKIES.get('sessionid')
    # Check if session is active
    if isSessionActive(sessionid) == False:
        return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
    object = request.data
    user_email = Session.objects.get(
        session_key=sessionid).get_decoded()['user_email']
    if user_email is None:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    user_exists = CustomUser.objects.get(email=user_email)
    current = UserData.objects.get(user_id=user_exists)
    current.media = []
    current.save()
    return Response({"Status": "OK"})


@api_view(['POST'])
def removeMedia(request):
    # get sessionid from request cookie
    sessionid = request.COOKIES.get('sessionid')
    # Check if session is active
    if isSessionActive(sessionid) == False:
        return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
    user_email = Session.objects.get(
        session_key=sessionid).get_decoded()['user_email']
    if user_email is None:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    # Expect email to be at 0
    # Expect Media to be at 1
    object = request.data
    user_exists = CustomUser.objects.get(email=user_email)
    current = UserData.objects.get(user_id=user_exists)
    cur_list = current.media

    ids = []
    types = []
    for elem in cur_list:
        ids.append(elem["id"])
        types.append(elem["media_type"])

    if str(object["id"]) in ids:
        indecies = [index for index, item in enumerate(ids) if item == str(object["id"])]
        for index in indecies:
            if types[index] == object["media_type"]:
                ids.pop(index)
                types.pop(index)
                new_list = []
                for i in range(len(ids)):
                    new_list.append({"id": ids[i], "media_type": types[i]})
                current.media = new_list
                current.save()
                return Response({"Status": "OK"}, status=status.HTTP_200_OK)
    return Response({"Status": "OK"})


@api_view(['POST'])
def saveBundle(request):
    # get sessionid from request cookie
    sessionid = request.COOKIES.get('sessionid')
    # Check if session is active
    if isSessionActive(sessionid) == False:
        return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
    user_email = Session.objects.get(
        session_key=sessionid).get_decoded()['user_email']
    if user_email is None:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    # Expect email to be at 0
    # Expect bundle to be at 1
    bundle = request.data
    user_exists = CustomUser.objects.get(email=user_email)
    current = UserData.objects.get(user_id=user_exists)
    current.bundle = bundle
    current.save()
    return Response({"Status": "OK"})


class returnUserData(generics.ListAPIView):
    def get(self, request):
        # # get sessionid from request cookie
        sessionid = request.COOKIES.get('sessionid')
        # Check if session is active
        if isSessionActive(sessionid) == False:
            return Response({'error': 'Session expired'}, status=status.HTTP_400_BAD_REQUEST)
        # Get user from session
        user_email = Session.objects.get(
            session_key=sessionid).get_decoded()['user_email']
        if user_email is None:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        user_exists = CustomUser.objects.get(email=user_email)
        output = UserData.objects.get(user_id=user_exists)
        serializer = UserDataSerializer(output)
        return Response(serializer.data)


@api_view(['POST'])
def returnInfo(request):
    object = request.data
    return Response(getData(object))


class newlyReleased(generics.ListAPIView):
    def get(self, request):

        # TV SHOWS
        url = "https://api.themoviedb.org/3/discover/tv?first_air_date_year=2023&include_adult=false&include_null_first_air_dates=false&language=en-US&page=1&sort_by=popularity.desc&watch_region=US"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NWNkNTI3OWYxN2M2NTkzMTIzYzcyZDA0ZTBiZWRmYSIsInN1YiI6IjY0NDg4NTgzMmZkZWM2MDU3M2EwYjk3MCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.VXG36aVRaprnsBeXXhjGq6RmRRoPibEuGsjkgSB-Q-c"
        }
        response = requests.get(url, headers=headers)
        new_shows = response.json()['results']

        # MOVIES
        url = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&primary_release_year=2023&sort_by=popularity.desc&watch_region=US"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NWNkNTI3OWYxN2M2NTkzMTIzYzcyZDA0ZTBiZWRmYSIsInN1YiI6IjY0NDg4NTgzMmZkZWM2MDU3M2EwYjk3MCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.VXG36aVRaprnsBeXXhjGq6RmRRoPibEuGsjkgSB-Q-c"
        }
        response = requests.get(url, headers=headers)
        new_movies = response.json()['results']

        # Need top 20, take the 20 most recent
        serialized_list = []
        for show in new_shows:
            if datetime.strptime(show['first_air_date'], '%Y-%m-%d') < datetime.now():
                serialized_list.append({
                    'title': show['name'],
                    'release_date': show['first_air_date'],
                    'poster_path': show['poster_path'],
                    'backdrop': show['backdrop_path'],
                    'rating': show['vote_average'],
                    'genres': show['genre_ids'],
                    'overview': show['overview'],
                    'media_type': 'tv',
                    'id': show['id']
                })
        for movie in new_movies:
            if datetime.strptime(movie['release_date'], '%Y-%m-%d') < datetime.now():
                serialized_list.append({
                    'title': movie['title'],
                    'release_date': movie['release_date'],
                    'poster_path': movie['poster_path'],
                    'backdrop': movie['backdrop_path'],
                    'rating': movie['vote_average'],
                    'genres': movie['genre_ids'],
                    'overview': movie['overview'],
                    'media_type': 'movie',
                    'id': movie['id']
                })
        sorted_data = sorted(
            serialized_list, key=lambda x: x['release_date'], reverse=True)
        recent_dicts = sorted_data[:20]
        return Response(recent_dicts, status=status.HTTP_200_OK)


def optimizeInTheBackground(media_list):
    url = "http://localhost:8000/optimize/"
    requests.post(url, json=media_list)


@api_view(['POST'])
def runOptimization(request):
    media_list = request.data
    sessionid = request.COOKIES.get('sessionid')
    user_email = Session.objects.get(
            session_key=sessionid).get_decoded()['user_email']
    if user_email is None:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    # get sessionid from request cookie
    user = CustomUser.objects.get(email=user_email)
    current = UserData.objects.get(user_id=user)
    budget = current.budget
    # Get info from media_list
    data = []
    for media in media_list:
        if media['media_type'] == "movie":
            id = media['id']
            api_key = "95cd5279f17c6593123c72d04e0bedfa"
            base_url = "https://api.themoviedb.org/3/"
            endpoint = "movie/"
            full_url = base_url + endpoint + \
                str(id) + "?api_key=" + api_key + "&language=en-US"
            response = requests.get(full_url)
            if response.status_code != 200:
                return None
            movie_data = response.json()
            temp = {}
            temp['title'] = movie_data['title']
            temp['release_date'] = movie_data['release_date']
            temp['poster_path'] = movie_data['poster_path']
            temp['backdrop'] = movie_data['backdrop_path']
            temp['rating'] = movie_data['vote_average']
            temp['genres'] = movie_data['genres']
            temp['overview'] = movie_data['overview']
            temp['media_type'] = "movie"
            temp['id'] = movie_data['id']
            streaming_providers = getStreamingProviderMovie(id)
            temp['streaming_providers'] = streaming_providers if streaming_providers != None else "Not Available"
            data.append(temp)
        else:
            id = media['id']
            api_key = "95cd5279f17c6593123c72d04e0bedfa"
            base_url = "https://api.themoviedb.org/3/"
            endpoint = "tv/"
            full_url = base_url + endpoint + \
                str(id) + "?api_key=" + api_key + "&language=en-US"
            response = requests.get(full_url)
            if response.status_code != 200:
                return None
            show_data = response.json()
            temp = {}
            temp['title'] = show_data['name']
            temp['release_date'] = show_data['first_air_date']
            temp['poster_path'] = show_data['poster_path']
            temp['backdrop'] = show_data['backdrop_path']
            temp['rating'] = show_data['vote_average']
            temp['genres'] = show_data['genres']
            temp['overview'] = show_data['overview']
            temp['media_type'] = "tv"
            temp['id'] = show_data['id']
            streaming_providers = getStreamingProviderShow(id)
            temp['streaming_providers'] = streaming_providers if streaming_providers != None else "Not Available"
            data.append(temp)

    providers, prices, services = modify_input(data)
    streamLine = optimize1(providers, prices, services, budget, data)
    # current.bundle.append(streamLine)
    # current.save()
    return Response(streamLine, status = status.HTTP_200_OK)


class StaffPicks(generics.ListAPIView):
    def get(self, request):
        staff_picks = StaffPick.objects.all()
        serialized_list = []
        for pick in staff_picks:
            if pick.Media_Type == "movie":
                id = pick.Media_ID
                api_key = "95cd5279f17c6593123c72d04e0bedfa"
                base_url = "https://api.themoviedb.org/3/"
                endpoint = "movie/"
                full_url = base_url + endpoint + \
                str(id) + "?api_key=" + api_key + "&language=en-US"
                response = requests.get(full_url)
                if response.status_code != 200:
                    continue
                movie_data = response.json()
                serialized_list.append({
                'title': movie_data['title'],
                'release_date': movie_data['release_date'],
                'poster_path': movie_data['poster_path'],
                'backdrop': movie_data['backdrop_path'],
                'rating': movie_data['vote_average'],
                'genres': movie_data['genres'],
                'overview': movie_data['overview'],
                'media_type': pick.Media_Type,
                'id': pick.Media_ID
                })  

            else:
                id = pick.Media_ID
                api_key = "95cd5279f17c6593123c72d04e0bedfa"
                base_url = "https://api.themoviedb.org/3/"
                endpoint = "tv/"
                full_url = base_url + endpoint + \
                    str(id) + "?api_key=" + api_key + "&language=en-US"
                response = requests.get(full_url)
                if response.status_code != 200:
                    continue
                show_data = response.json()
                serialized_list.append({
                'title': show_data['name'],
                'release_date': show_data['first_air_date'],
                'poster_path': show_data['poster_path'],
                'backdrop': show_data['backdrop_path'],
                'rating': show_data['vote_average'],
                'genres': show_data['genres'],
                'overview': show_data['overview'],
                'media_type': pick.Media_Type,
                'id': pick.Media_ID
                })
    
        return Response(serialized_list, status=status.HTTP_200_OK)

class seeServices(generics.ListAPIView):
        def get(self, request):
            search_query = request.query_params.get('search', None)
            if search_query is None:
                return Response({'error': 'Missing search query'}, status=status.HTTP_400_BAD_REQUEST)

            service_images = pd.read_csv('api/random/serviceImages.csv')
            service_info = pd.read_csv('api/random/pricing - Copy of Sheet1-2.csv')

            # For each row in service_info, find the corresponding image in service_images by matching service_name in serviceImages to Name in service_info
            # Output the title, price, image, and link into a dict to return
            ## make a list of all of the elements in service_info["Name"]

            services = service_info['Name'].tolist()
            # find top four services closest to search_query
            top_four = []
            for service in services:
                top_four.append((service, fuzz.ratio(service, search_query)))
            top_four = sorted(top_four, key=lambda x: x[1], reverse=True)[:4]
            print(top_four)
            output = []
            for tuple in top_four:
                service = tuple[0]
                service_name = service_info.loc[service_info['Name'] == service]['Name'].values[0]
                service_link = service_info.loc[service_info['Name'] == service]['Link'].values[0]
                service_packages = []
                i = service_info.index[service_info['Name'] == service].tolist()[0]
                j = 1
                while j < 9:
                    if not pd.isna(service_info.iloc[i, j]) and not pd.isna(service_info.iloc[i, j+1]):
                        service_packages.append({
                            "Version": service_info.iloc[i,j],
                            "Price": service_info.iloc[i,j+1],
                        })
                    j += 2
                if service_packages == []:
                    service_packages.append({"Version": "Standard", "Price": 0.00})
                service_image = service_images.loc[service_images['service_name'] == service_name]['logo_path'].values
                output.append({
                    "Name": service_name,
                    "Image": service_image,
                    "Link": service_link,
                    "Packages": service_packages
                })
            print(output)
            return Response(output, status=status.HTTP_200_OK)

class AllServices(generics.ListAPIView):
    def get(self, request):
        service_images = pd.read_csv('api/random/serviceImages.csv')
        service_info = pd.read_csv('api/random/pricing - Copy of Sheet1-2.csv')

        service_info = service_info.fillna("Not Available")

        service_info['Package 1'] = service_info['Package 1'].replace('Not Available', 'Free')
        service_info['Add-On'] = service_info['Add-On'].map({0: 'No', 1: 'Yes'})

        service_info = service_info.fillna("Not Available")
        # Merge service_info and service_images based on service name

        aggregated_table = pd.merge(service_info, service_images, 
                                    left_on='Name', right_on='service_name', 
                                    how='inner').drop(columns=['service_name', 'id'])

        return Response(aggregated_table.to_dict(), status=status.HTTP_200_OK)
        

class getAllUpcoming(generics.ListAPIView):
    def get(self, request):
        release_year = datetime.now().year
        # TV SHOWS
        url = "https://api.themoviedb.org/3/discover/tv?first_air_date.gte=" + str(datetime.now().date()) + "&include_adult=false&include_null_first_air_dates=false&language=en-US&page=1&sort_by=popularity.desc"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NWNkNTI3OWYxN2M2NTkzMTIzYzcyZDA0ZTBiZWRmYSIsInN1YiI6IjY0NDg4NTgzMmZkZWM2MDU3M2EwYjk3MCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.VXG36aVRaprnsBeXXhjGq6RmRRoPibEuGsjkgSB-Q-c"
        }
        response = requests.get(url, headers=headers)
        new_shows = response.json()['results']

        # MOVIES
        url = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&primary_release_date.gte=" + str(datetime.now().date()) + "&sort_by=popularity.desc"
        
        response = requests.get(url, headers=headers)
        new_movies = response.json()['results']

        # NEED TO FIND SHOWS BEING RELEASED THIS WEEK
        output = []
        for show in new_shows:
            print(str(datetime.strptime(show['first_air_date'][:10], format_str).date()) + " " + str(datetime.now().date()) + " " + show['name'])
            # Check if it is released this week
            if show['first_air_date'] is not None and datetime.strptime(show['first_air_date'][:10], format_str).date() >= datetime.now().date():
                show["media_type"] = "tv"
                show["release_date"] = show["first_air_date"]
                output.append(show)


        for movie in new_movies:
                        # Check if it is released this week
            if movie['release_date'] is not None and datetime.strptime(movie['release_date'][:10], format_str).date() >= datetime.now().date():
                # Check if it is on a subscription
                movie['media_type'] = "movie"
                output.append(movie)
        
        sorted_data = sorted(output, key=lambda x: x["release_date"])
        return Response(sorted_data, status=status.HTTP_200_OK)


