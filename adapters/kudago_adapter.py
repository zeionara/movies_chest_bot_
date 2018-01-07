import time
import requests
from collections import namedtuple

MovieHeader = namedtuple('MovieHeader','title href id')
MovieExtendedHeader = namedtuple('MovieExtendedHeader','title href id')
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
    url = 'https://kudago.com/public-api/v1.3/movies/?location=spb&lang=en&page_size=100&actual_since={}&actual_until={}&fields=original_title,year,title,genres,id'.format(
            current_time - 4*week_length, current_time + week_length)

    response = requests.get(url)
    result = []

    for movie in response.json()['results']:
        if genre is not None and not intersects(genre, movie['genres']):
            continue
        if movie['original_title'] != '':
            result.append(MovieExtendedHeader(movie['original_title'] + ' (' + str(movie['year']) + ')', 'n/a', movie['id']))
        else:
            result.append(MovieExtendedHeader(movie['title'] + ' (' + str(movie['year']) + ')', 'n/a', movie['id']))

    return result

def get_movie_details(id):
    response = requests.get('https://kudago.com/public-api/v1.2/movies/' + str(id) + '/?fields=description,body_text,poster,trailer')
    return response.json()

#print(get_actual_movies())
#print(get_movie_details(1441))
