#
#python
#

import requests
from collections import namedtuple
import telegram

#
#odm
#

from user import get_user, create_user

#
#resources
#

from constants import top_movies_xml_path, states, delimiter, omdb_api_key, msg_no_more_movies
from keyboard_markups import action_reply_markup, action_reply_markup_extended, action_reply_markup_reduced, action_reply_markup_extremely_reduced
from shared import ya, pa

#
#managers
#

from message_manager import send_chunked, send_plain, send_chunked_forked
from db_connection_manager import get_session

#
#caching
#

from redis_connector import get_from_redis, write_to_redis

#
#tools
#

from html_parcing import remove_tags
from string_converting import stringify_advanced_movie_info, chunkstring
from collection_converting import list_to_movie_header

#
#adapters
#

import youtube_adapter
import kudago_adapter
import kinopoisk_adapter
import afisha_adapter
from top_movies_adapter import get_top_movies

Movie = namedtuple('Movie','title poster description trailer')
MovieHeader = namedtuple('MovieHeader','title href')
MovieExtendedHeader = namedtuple('MovieExtendedHeader','title href id')

#
#get movie info via basic information from user's object
#

def get_standart_movie_info(user, session):
    tracker = user.tracker
    genre = user.genre

    movie = list_to_movie_header(user.movies[user.indexes[tracker][genre]])

    if tracker == 'yup':
        return ya.get_movie_by_header(movie)
    elif tracker == 'pbay' or tracker == 'mine' or tracker == 'act':
        return Movie(movie.title, None, 'no description found', youtube_adapter.get_trailer(movie.title))

#
#try to get info about movie from omdb (primary) or from kinopoisk
#

def get_advanced_movie_info_by_title(title):

    #Title comes in format: "Good time (2017)"

    arr = title.split(' (')
    name_original = arr[0]
    name = arr[0].replace(' ','+')

    try:
        year = arr[1].replace(')','').replace(' ','')
    except IndexError:
        url = 'http://www.omdbapi.com/?apikey={}&t={}&plot=full'.format(omdb_api_key, name)
    else:
        url = 'http://www.omdbapi.com/?apikey={}&t={}&y={}&plot=full'.format(omdb_api_key, name, year)

    response = requests.get(url)
    result = ''
    dicti = response.json()

    if dicti['Response'] == 'False':
        kinopoisk_dicti = kinopoisk_adapter.get_movie_info(title)
        if kinopoisk_dicti is not None:
            kinopoisk_dicti['Response'] = 'True'
            return kinopoisk_dicti

    if 'Title' not in dicti:
        dicti['Title'] = name_original

    return dicti

#
#send minimal movie info
#

def send_standart_movie_info(bot, user, session, redis_key, href):
    user.imdb_id = None
    user.current_title = redis_key

    movie = get_standart_movie_info(user, session)

    content = movie.title + '\n\n\n' + movie.trailer + '\n\n\n' + movie.description + '\n\n\nHref: ' + href

    send_chunked(bot = bot, chat_id = user.chat_id, message = content, image = movie.poster, reply_markup = action_reply_markup)

    movie_info = {}
    movie_info['Poster'] = movie.poster
    movie_info['Trailer'] = movie.trailer
    movie_info['Title'] = movie.title
    movie_info['Href'] = href
    movie_info['Description'] = movie.description

    write_to_redis(redis_key, movie_info, False)

    session.flush()

#
#send movie info got from omdb
#

def send_advanced_movie_info(bot, user, session, advanced_info, redis_key, href):
    user.imdb_id = advanced_info.get('imdbID')
    user.current_title = redis_key

    trailer = youtube_adapter.get_trailer(advanced_info['Title'])

    poster = advanced_info['Poster']
    content = advanced_info['Title'] + '\n\n\nTrailer: ' + trailer + '\n\n\n' + stringify_advanced_movie_info(advanced_info) + '\n\n\nHref: ' + href

    send_chunked(bot = bot, chat_id = user.chat_id, message = content, image = poster, reply_markup = action_reply_markup_extended)

    advanced_info['Trailer'] = trailer
    advanced_info['Href'] = href

    write_to_redis(redis_key, advanced_info, False)
    session.flush()

#
#send movie info without additional buttons, which consider movies list, such as next and flush
#

def send_advanced_single_movie_info(bot, user, session, advanced_info):
    if 'Year' in advanced_info:
        redis_key = advanced_info['Title'] + ' (' + advanced_info['Year'] + ')'
    else:
        redis_key = advanced_info['Title']

    trailer = youtube_adapter.get_trailer(advanced_info['Title'])

    user.current_title = redis_key

    poster = advanced_info.get('Poster')
    content = advanced_info['Title'] + '\n\n\nTrailer: ' + trailer + '\n\n\n' + stringify_advanced_movie_info(advanced_info)

    send_chunked_forked(bot = bot, chat_id = user.chat_id, message = content,\
        reply_markups = [action_reply_markup_reduced, action_reply_markup_extremely_reduced],\
        conditions = [advanced_info.get('imdbID') is not None], image = poster)

    advanced_info['Trailer'] = trailer

    write_to_redis(redis_key, advanced_info, True)

    session.flush()

#
#general method for sending movie info to user just by their chat_id
#

def send_movie_info(bot, user, session):
    chat_id = user.chat_id
    tracker = user.tracker
    genre = user.genre

    #get header of the actual movie, if it is impossible, then tell user about it

    try:
        movie = list_to_movie_header(user.movies[user.indexes[tracker][genre]])
    except IndexError:
        send_plain(bot, chat_id, msg_no_more_movies)
        return

    #otherwise get movie info from the cache, if it is possible, then send message

    cached_movie_info = get_from_redis(movie.title)

    if cached_movie_info is not None:

        if 'Schedule' in cached_movie_info:
            afisha_adapter.make_html_schedule(movie.id, bot, chat_id)

        user.imdb_id = cached_movie_info.get('imdbID')
        user.current_title = movie.title

        poster = cached_movie_info.get('Poster')
        content = cached_movie_info.get('Title') + '\n\n\n' + stringify_advanced_movie_info(cached_movie_info) + '\n\n\n'

        send_chunked_forked(bot = bot, chat_id = chat_id, message = content,\
            reply_markups = [action_reply_markup_extended, action_reply_markup], conditions = ['imdbID' in cached_movie_info], image = poster)

        return

    #otherwise get movie info from omdb

    advanced_info = get_advanced_movie_info_by_title(movie.title)

    if tracker == 'act':
        advanced_info['Schedule'] = afisha_adapter.make_html_schedule(movie.id, bot, chat_id)

    session.flush()

    #and finally, send message

    if advanced_info['Response'] == 'False':
        send_standart_movie_info(bot, user, session, movie.title, movie.href)
    else:
        send_advanced_movie_info(bot, user, session, advanced_info, movie.title, movie.href)

#
#prepare and send first message with movie info just after user have selected a tracker
#

def send_first_movie_msg(bot, user, session, tracker):
    if tracker == 'pbay' or tracker == 'mine' or tracker == 'act':
        genre = 'any'

        user.genre = genre
        user.state = states['iterating']

        if user.indexes[user.tracker].get(genre) is None:
            user.indexes[user.tracker][genre] = 0
            user.pages[user.tracker][genre] = 1
        else:
            increase_index(user, session)

        update_movies(user, session)

        session.flush()

        send_movie_info(bot, user, session)
#
#load movies list from an external source
#

def load_page(tracker, genre, page):

    redis_key = str(tracker) + delimiter + str(genre) + delimiter + str(page)

    if tracker == 'yup':
        movies = ya.get_movies_by_genre(genre, page)
    elif tracker == 'pbay':
        movies = pa.get_movies_by_page(page)
    elif tracker == 'mine':
        movies = get_top_movies(top_movies_xml_path)
    elif tracker == 'act':
        movies = afisha_adapter.get_actual_movies(page)

    return movies

#
#load movies list from an external source and cache it in redis
#

def cache_page(tracker, genre, page):
    redis_key = str(tracker) + delimiter + str(genre) + delimiter + str(page)
    cached_movies = get_from_redis(redis_key)

    if cached_movies is not None:
        return cached_movies

    movies = load_page(tracker, genre, page)
    write_to_redis(redis_key, movies, True)
    return movies

#
#load movies list from an external source, cache it in redis and assign it to a user
#

def update_movies(user, session):
    tracker = user.tracker
    genre = user.genre
    page = user.pages[tracker][genre]

    user.movies = cache_page(tracker, genre, page)

    session.flush()

#
#move to next movie in user's list
#

def increase_index(user, session):
    tracker = user.tracker
    genre = user.genre

    if user.indexes[tracker][genre] < len(user.movies) - 1:
        user.indexes[tracker][genre] += 1
        session.flush()
    else:
        user.indexes[tracker][genre] = 0
        user.pages[tracker][genre] += 1
        session.flush()
        update_movies(user, session)
