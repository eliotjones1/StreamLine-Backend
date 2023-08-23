import requests
import json
from rest_framework.response import Response
from rest_framework import generics, status
import pandas as pd
import numpy as np
from .models import *
from settings.models import *
from .serializers import *
from surprise import Reader, Dataset, SVD
from authentication.models import CustomUser
from api.functions import *

DATA_HAS_BEEN_GENERATED = 0

def returnRecs(target_user_id, subscriptions):
    cur_ratings = MediaRatings.objects.all().values()
    data = pd.DataFrame.from_records(cur_ratings)
    data = data.drop(columns = ['id'])
    reader = Reader(rating_scale=(1, 10))
    

    movie_data = data[data['media_type'] == 'movie']
    movie_data = movie_data[movie_data['streaming_providers'].apply(lambda providers: any(service in subscriptions for service in providers))]

    tv_data = data[data['media_type'] == 'tv']
    tv_data = tv_data[tv_data['streaming_providers'].apply(lambda providers: any(service in subscriptions for service in providers))]
    data_movies = Dataset.load_from_df(movie_data[["media_id", "rating", "user_id", "streaming_providers"]], reader)
    trainset_movies = data_movies.build_full_trainset()

    # Create a separate Dataset and Trainset for TV shows
    data_tv_shows = Dataset.load_from_df(tv_data[["media_id", "rating", "user_id", "streaming_providers"]], reader)
    trainset_tv_shows = data_tv_shows.build_full_trainset()


    algo_movies = SVD()
    algo_movies.fit(trainset_movies)

    algo_tv_shows = SVD()
    algo_tv_shows.fit(trainset_tv_shows)


    target_user_inner_id_movies = trainset_movies.to_inner_uid(target_user_id)
    target_user_inner_id_tv_shows = trainset_tv_shows.to_inner_uid(target_user_id)

    similar_users_movies = algo_movies.get_neighbors(target_user_inner_id_movies, 20)
    similar_user_ids_movies = [trainset_movies.to_raw_uid(inner_id) for inner_id in similar_users_movies]

    similar_users_tv_shows = algo_tv_shows.get_neighbors(target_user_inner_id_tv_shows, 20)
    similar_user_ids_tv_shows = [trainset_tv_shows.to_raw_uid(inner_id) for inner_id in similar_users_tv_shows]

    recommendation_ids_movies = []
    recommendation_ids_tv_shows = []
    
    for user_id in similar_user_ids_movies:
        user_recs = algo_movies.get_top_n(trainset_movies.ur[trainset_movies.to_inner_uid(user_id)], n=20)
        for rec in user_recs:
            recommendation_ids_movies.extend(rec[0])

    for user_id in similar_user_ids_tv_shows:
        user_recs = algo_tv_shows.get_top_n(trainset_tv_shows.ur[trainset_tv_shows.to_inner_uid(user_id)], n=20)
        for rec in user_recs:
            recommendation_ids_tv_shows.extend(rec[0])

    recommendation_ids_movies = list(set([id for id in recommendation_ids_movies if not MediaRatings.objects.filter(media_id=id, user_id=target_user_id, media_type = "movie").exists()]))
    recommendation_ids_tv_shows = list(set([id for id in recommendation_ids_tv_shows if not MediaRatings.objects.filter(media_id=id, user_id=target_user_id, media_type = "tv").exists()]))

    return {
        "movies": recommendation_ids_movies,
        "tv_shows": recommendation_ids_tv_shows
    }


def recOutput(recs, subscriptions):
    Output = {}
    for sub in subscriptions:
        Output[sub] = []
    for rec in recs["tv_shows"]:
        object = {}
        object["media_type"] = "tv"
        object["id"] = rec
        temp = getData(object)
        if temp is not None:
            Output[temp["streaming_providers"][0]].append(temp)
    for rec in recs["movies"]:
        object = {}
        object["media_type"] = "movie"
        object["id"] = rec
        temp = getData(object)
        if temp is not None:
            Output[temp["streaming_providers"][0]].append(temp)
    return Output


def generateData(page_input):
    if DATA_HAS_BEEN_GENERATED == 1:
        print("Data has been generated already")
        return 0
    else:
        #get all users
        users = CustomUser.objects.all()
        #get all media

        # Get popular movies from TMDB

        url = "https://api.themoviedb.org/3/movie/popular?language=en-US&page=" + page_input
        print(url)

        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NWNkNTI3OWYxN2M2NTkzMTIzYzcyZDA0ZTBiZWRmYSIsInN1YiI6IjY0NDg4NTgzMmZkZWM2MDU3M2EwYjk3MCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.VXG36aVRaprnsBeXXhjGq6RmRRoPibEuGsjkgSB-Q-c"
        }

        response_movies = requests.get(url, headers=headers)


        url = "https://api.themoviedb.org/3/tv/popular?language=en-US&page=" + page_input

        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NWNkNTI3OWYxN2M2NTkzMTIzYzcyZDA0ZTBiZWRmYSIsInN1YiI6IjY0NDg4NTgzMmZkZWM2MDU3M2EwYjk3MCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.VXG36aVRaprnsBeXXhjGq6RmRRoPibEuGsjkgSB-Q-c"
        }

        response_tv = requests.get(url, headers=headers)
        movie_pop = response_movies.json()
        tv_pop = response_tv.json()

        top_movies = movie_pop['results']
        top_tv = tv_pop['results']

        # Create a list of all the media
        # For each entry in media_list
        # for each user in the database
        # Generate a random number between 1 and 10 from normal distribution centered around vote_average of media
        # Create a new MediaRatings entry with the user, media, and rating
        # Save the entry

        for entry in top_movies:
            for user in users:
                # Generate a random number between 1 and 10 from normal distribution centered around vote_average of media
                rating = round(np.random.normal(entry['vote_average'], 1))             
                new = MediaRatings()
                new.media_id = entry['id']
                new.user_id = user.to_json()
                new.rating = rating
                new.media_type = "movie"
                new.streaming_providers = getStreamingProviderMovie(entry['id'])
                # Save the entry
                new.save()
            if 'title' in entry:
                print(entry['title'] + " was a success!")
            else:
                print(entry['name'] + " was a success!")

        for entry in top_tv:
            for user in users:
                rating = round(np.random.normal(entry['vote_average'], 1))
                new = MediaRatings()
                new.media_id = entry['id']
                new.user_id = user.to_json()
                new.rating = rating
                new.media_type = "tv"
                new.streaming_providers = getStreamingProviderShow(entry['id'])
                new.save()
            if 'title' in entry:
                print(entry['title'] + " was a success!")
            else:
                print(entry['name'] + " was a success!")

        return 1










