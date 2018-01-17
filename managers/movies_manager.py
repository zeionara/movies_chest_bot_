import requests
from collections import namedtuple

#from shared import users
from user import get_user, create_user
from db_connection_manager import get_session

from shared import ya
from shared import pa

from string_converting import chunkstring

from redis_connector import get_from_redis
from redis_connector import write_to_redis

from constants import top_movies_xml_path
from constants import states
from constants import delimiter
from constants import omdb_api_key

from html_parcing import remove_tags

from keyboard_markups import action_reply_markup
from keyboard_markups import action_reply_markup_extended
from keyboard_markups import action_reply_markup_reduced
from keyboard_markups import action_reply_markup_extremely_reduced

from string_converting import stringify_advanced_movie_info

import youtube_adapter
import kudago_adapter
import kinopoisk_adapter

from top_movies_adapter import get_top_movies

from actual_movies_filter import save_movie_today_schedule

import afisha_adapter

Movie = namedtuple('Movie','title poster description trailer')
MovieHeader = namedtuple('MovieHeader','title href')
MovieExtendedHeader = namedtuple('MovieExtendedHeader','title href id')

#
#get movie info via basic information from user's object
#

def get_standart_movie_info(chat_id):
    user = get_user(chat_id)
    session = get_session()

    #user = users[chat_id]
    tracker = user.tracker
    genre = user.genre



    if tracker == 'yup':
        movie = MovieHeader(*(user.movies[user.indexes[user.tracker][user.genre]]))
        return ya.get_movie_by_header(movie)
    elif tracker == 'pbay' or user.tracker == 'mine':
        movie = MovieHeader(*(user.movies[user.indexes[user.tracker][user.genre]]))
        title = movie.title
        trailer = youtube_adapter.get_trailer(title)
        return Movie(title, None, 'no description found', trailer)
    elif tracker == 'act':
        movie = MovieExtendedHeader(*(user.movies[user.indexes[user.tracker][user.genre]]))
        movie_details = kudago_adapter.get_movie_details(movie.id)
        return Movie(movie.title, movie_details['poster']['image'],
                remove_tags(movie_details['description'] + movie_details['body_text']), movie_details['trailer'])

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
#get movie info as a set of messages
#

def send_standart_movie_info(bot, chat_id, redis_key, href):
    user = get_user(chat_id)
    session = get_session()

    user.imdb_id = None
    user.current_title = redis_key
    movie = get_standart_movie_info(chat_id)

    if movie.poster is not None:
        bot.sendPhoto(chat_id, movie.poster)

    content = movie.title + '\n\n\n' + movie.trailer + '\n\n\n' + movie.description + '\n\n\nHref: ' + href

    chunks = chunkstring(content)
    for chunk in chunks[:-1]:
        bot.sendMessage(chat_id, chunk)

    bot.sendMessage(chat_id, chunks[-1], reply_markup = action_reply_markup)

    movie_info = {}
    movie_info['Poster'] = movie.poster
    movie_info['Trailer'] = movie.trailer
    movie_info['Title'] = movie.title
    movie_info['Href'] = href
    movie_info['Description'] = movie.description

    write_to_redis(redis_key, movie_info, False)

    session.flush()

def send_advanced_movie_info(bot, chat_id, advanced_info, redis_key, href):
    user = get_user(chat_id)
    session = get_session()

    user.imdb_id = advanced_info.get('imdbID')
    user.current_title = redis_key

    trailer = youtube_adapter.get_trailer(advanced_info['Title'])

    if advanced_info['Poster'] is not None:
        print('poster : ',advanced_info['Poster'])
        bot.sendPhoto(chat_id, advanced_info['Poster'])

    #schedule = get_movie_today_schedule()
    print(advanced_info)
    print(trailer)
    print(stringify_advanced_movie_info(advanced_info))
    print(href)
    bot.sendMessage(chat_id, advanced_info['Title'] + '\n\n\nTrailer: ' + trailer + '\n\n\n' + \
                    stringify_advanced_movie_info(advanced_info) + '\n\n\nHref: ' + href, reply_markup = action_reply_markup_extended)

    advanced_info['Trailer'] = trailer
    advanced_info['Href'] = href

    #if 'Schedule' in advanced_info:
    #    write_to_redis(redis_key, advanced_info, True)

    write_to_redis(redis_key, advanced_info, False)
    session.flush()

def send_advanced_single_movie_info(bot, chat_id, advanced_info):
    user = get_user(chat_id)
    session = get_session()

    print(advanced_info)
    if 'Year' in advanced_info:
        redis_key = advanced_info['Title'] + ' (' + advanced_info['Year'] + ')'
    else:
        redis_key = advanced_info['Title']
    trailer = youtube_adapter.get_trailer(advanced_info['Title'])

    user.current_title = redis_key

    if advanced_info.get('Poster') is not None:
        bot.sendPhoto(chat_id, advanced_info['Poster'])

    if advanced_info.get('imdbID') is not None:
        user.imdb_id = advanced_info['imdbID']
        bot.sendMessage(chat_id, advanced_info['Title'] + '\n\n\nTrailer: ' + trailer + '\n\n\n' + \
                        stringify_advanced_movie_info(advanced_info), reply_markup = action_reply_markup_reduced)
    else:
        bot.sendMessage(chat_id, advanced_info['Title'] + '\n\n\nTrailer: ' + trailer + '\n\n\n' + \
                        stringify_advanced_movie_info(advanced_info), reply_markup = action_reply_markup_extremely_reduced)

    advanced_info['Trailer'] = trailer

    write_to_redis(redis_key, advanced_info, True)

    session.flush()

def send_movie_info(bot, chat_id):
    user = get_user(chat_id)
    session = get_session()

    try:
        print(user.movies)
        movie_list = user.movies[user.indexes[user.tracker][user.genre]]
        print(movie_list)
        print(len(movie_list))
        if len(movie_list) == 2:
            movie = MovieHeader(*movie_list)
        elif len(movie_list) == 3:
            movie = MovieExtendedHeader(*movie_list)
        print(movie)
    except IndexError:
        bot.sendMessage(chat_id, 'There are no more movies')
        return

    cached_movie_info = get_from_redis(movie.title)

    if cached_movie_info is not None:
        print(cached_movie_info)

        if 'Schedule' in cached_movie_info:
            afisha_adapter.make_html_schedule(movie.id, bot, chat_id)

        if cached_movie_info['Poster'] is not None:
            bot.sendPhoto(chat_id, cached_movie_info['Poster'])
        user.imdb_id = cached_movie_info.get('imdbID')
        user.current_title = movie.title

        content = cached_movie_info['Title'] + '\n\n\n' + stringify_advanced_movie_info(cached_movie_info) + '\n\n\n'

        chunks = chunkstring(content)
        for chunk in chunks[:-1]:
            bot.sendMessage(chat_id, chunk)

        if 'imdbID' in cached_movie_info:
            bot.sendMessage(chat_id, chunks[-1], reply_markup = action_reply_markup_extended)
        else:
            bot.sendMessage(chat_id, chunks[-1], reply_markup = action_reply_markup)
        return

    advanced_info = get_advanced_movie_info_by_title(movie.title)

    if user.tracker == 'act':
        schedule_href = afisha_adapter.make_html_schedule(movie.id, bot, chat_id)
        advanced_info['Schedule'] = schedule_href

        #if 'Schedule' in advanced_info:
        #    write_to_redis(redis_key, advanced_info, True)

    if user.tracker == 'yup' or user.tracker == 'mine' or user.tracker == 'act':
        href = movie.href
    elif user.tracker == 'pbay':
        href = pa.url + movie.href

    session.flush()


    if advanced_info['Response'] == 'False':
        send_standart_movie_info(bot, chat_id, movie.title, href)
    else:
        send_advanced_movie_info(bot, chat_id, advanced_info, movie.title, href)



def send_first_movie_msg(bot, chat_id, tracker):
    user = get_user(chat_id)
    session = get_session()


    if tracker == 'pbay' or tracker == 'mine' or tracker == 'act':
        genre = 'any'
        user.genre = genre
        user.state = states['iterating']
        print('Yohoho')

        if user.indexes[user.tracker].get(genre) is None:
            user.indexes[user.tracker][genre] = 0
            user.pages[user.tracker][genre] = 1
        else:
            increase_index(chat_id)

        update_movies(chat_id)

        session.flush()

        send_movie_info(bot, chat_id)
#
#other needed methods
#

def update_movies(chat_id):

    user = get_user(chat_id)
    session = get_session()

    tracker = user.tracker
    genre = user.genre
    page = user.pages[tracker][genre]

    redis_key = str(tracker) + delimiter + str(genre) + delimiter + str(page)
    print('iop1')
    cached_movies = get_from_redis(redis_key)
    print('iop2')
    if cached_movies is not None:
        user.movies = cached_movies
        return

    if tracker == 'yup':
        movies = ya.get_movies_by_genre(genre, page)
    elif tracker == 'pbay':
        movies = pa.get_movies_by_page(page)
    elif tracker == 'mine':
        movies = get_top_movies(top_movies_xml_path)
    elif tracker == 'act':
        movies = afisha_adapter.get_actual_movies(page)
        #movies = kudago_adapter.get_filtered_actual_movies(genre)
    print('iop3')
    write_to_redis(redis_key, movies, True)
    print('iop4')
    user.movies = movies
    print('iop5')
    session.flush()

def cache_page(tracker, genre, page):

    redis_key = str(tracker) + delimiter + str(genre) + delimiter + str(page)

    print('Caching page {}'.format(redis_key))
    print('---a')
    cached_movies = get_from_redis(redis_key)
    print('---b')
    if cached_movies is not None:
        print('already have it')
        return
    print('---c')
    if tracker == 'yup':
        movies = ya.get_movies_by_genre(genre, page)
    elif tracker == 'pbay':
        movies = pa.get_movies_by_page(page)
    elif tracker == 'mine':
        movies = get_top_movies(top_movies_xml_path)
    elif tracker == 'act':
        movies = afisha_adapter.get_actual_movies(page)
        #movies = kudago_adapter.get_actual_movies(genre)
    print('---d')
    print(movies)
    write_to_redis(redis_key, movies, True)
    print('---e')

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
        #movies = kudago_adapter.get_actual_movies(genre)

    return movies
    #write_to_redis(redis_key, movies, True)

def increase_index(chat_id):
    user = get_user(chat_id)
    session = get_session()

    #user = users[chat_id]

    tracker = user.tracker
    genre = user.genre

    if user.indexes[tracker][genre] < len(user.movies) - 1:
        user.indexes[tracker][genre] += 1
    else:
        user.indexes[tracker][genre] = 0
        user.pages[tracker][genre] += 1
        update_movies(chat_id)

    session.flush()
