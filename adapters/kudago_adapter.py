import sys


sys.path.append('../tools/')
sys.path.append('../resources/')

from actual_movies_filter import cut_title

import time
import requests
from collections import namedtuple
import mirage_cinema_adapter
import kinopik_adapter

from actual_movies_filter import get_cinemas_query_part, get_movie_schedule, check_actual_movies, get_movie_today_schedule, get_whole_schedule, save_movie_today_schedule, save_movie_today_schedule

MovieHeader = namedtuple('MovieHeader','title href id')
MovieExtendedHeader = namedtuple('MovieExtendedHeader','title href id original_title')
week_length = 604800

def intersects(genre, genre_list):
    for genre_description in genre_list:
        if genre_description['name'] == genre:
            return True
    return False

def get_actual_movies(genre = None):
    global week_length

    if genre is not None:
        genre = genre.lower()

    current_time = int(time.time())
    url = ('https://kudago.com/public-api/v1.3/movies/?location=spb&lang=en&page_size=100&actual_'+
            'since={}&actual_until={}&fields=original_title,year,title,genres,id'+get_cinemas_query_part()).format(
            current_time - int(week_length/7), current_time + week_length)

    response = requests.get(url)
    result = []

    for movie in response.json()['results']:
        if genre is not None and not intersects(genre, movie['genres']):
            continue
        #if movie['original_title'] != '':
        result.append(MovieExtendedHeader(movie['title'] + ' (' + str(movie['year']) + ')', 'n/a', movie['id'], movie['original_title']))
        #else:
            #result.append(MovieExtendedHeader(movie['title'] + ' (' + str(movie['year']) + ')', 'n/a', movie['id'], 'no schedule'))

    return result



def get_movie_details(id):
    response = requests.get('https://kudago.com/public-api/v1.2/movies/' + str(id) + '/?fields=title,description,body_text,poster,trailer')
    dicti = response.json()
    dicti['description'] += '\n\n' + save_movie_today_schedule(cut_title(dicti['title'])) + '\n'
    return dicti



def get_filtered_actual_movies(genre):
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    whole_schedule = get_whole_schedule()
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

    movies = get_actual_movies(genre)
    print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    #print(movies)
    result = []
    for movie in movies:
        cutted_title = cut_title(movie.title)
        #print('checking ',cutted_title)
        keys = list(whole_schedule.keys())
        if (cutted_title in whole_schedule[keys[0]]['Mirage cinema']) or (cutted_title in whole_schedule[keys[0]]['Kinopik']):
            result.append(movie)

            #print('norm',cutted_title)
            #if cutted_title in whole_schedule['Mirage cinema']:
            #    print(whole_schedule['Mirage cinema'][cutted_title])
            #if cutted_title in whole_schedule['Kinopik']:
            #    print(whole_schedule['Kinopik'][cutted_title])
    print(result)
    return result

#print(save_movie_today_schedule('Величайший шоумен'))
#movies = get_filtered_actual_movies()
#print(movies)
#for movie in movies:
    #print(movie.title)
    #print(get_movie_today_schedule(cut_title(movie.title)))
#get_movie_schedule(3014, 1, 10)
#check_actual_movies(get_actual_movies(), 1, 10)
#print(get_movie_details(1441))
