import requests
from collections import namedtuple

from shared import users
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

Movie = namedtuple('Movie','title poster description trailer')
MovieHeader = namedtuple('MovieHeader','title href')

#
#get movie info via basic information from user's object
#

def get_standart_movie_info(chat_id):

    user = users[chat_id]
    tracker = user.tracker
    genre = user.genre

    if tracker == 'yup':
        return ya.get_movie_by_header(user.movies[user.indexes[tracker][genre]])
    elif tracker == 'pbay' or users[chat_id].tracker == 'mine':
        title = user.movies[user.indexes[tracker][genre]].title
        trailer = youtube_adapter.get_trailer(title)
        return Movie(title, None, 'no description found', trailer)
    elif tracker == 'act':
        movie = user.movies[user.indexes[tracker][genre]]
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
        kinopoisk_dicti['Response'] = 'True'
        if kinopoisk_dicti is not None:
            return kinopoisk_dicti

    if 'Title' not in dicti:
        dicti['Title'] = name_original

    return dicti

#
#get movie info as a set of messages
#

def send_standart_movie_info(bot, chat_id, redis_key, href):

    users[chat_id].imdb_id = None
    users[chat_id].current_title = redis_key
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

def send_advanced_movie_info(bot, chat_id, advanced_info, redis_key, href):

    users[chat_id].imdb_id = advanced_info.get('imdbID')
    users[chat_id].current_title = redis_key

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

    if 'Schedule' in advanced_info:
        write_to_redis(redis_key, advanced_info, True)
    else:
        write_to_redis(redis_key, advanced_info, False)

def send_advanced_single_movie_info(bot, chat_id, advanced_info):
    print(advanced_info)
    if 'Year' in advanced_info:
        redis_key = advanced_info['Title'] + ' (' + advanced_info['Year'] + ')'
    else:
        redis_key = advanced_info['Title']
    trailer = youtube_adapter.get_trailer(advanced_info['Title'])

    users[chat_id].current_title = redis_key

    if advanced_info.get('Poster') is not None:
        bot.sendPhoto(chat_id, advanced_info['Poster'])

    if advanced_info.get('imdbID') is not None:
        users[chat_id].imdb_id = advanced_info['imdbID']
        bot.sendMessage(chat_id, advanced_info['Title'] + '\n\n\nTrailer: ' + trailer + '\n\n\n' + \
                        stringify_advanced_movie_info(advanced_info), reply_markup = action_reply_markup_reduced)
    else:
        bot.sendMessage(chat_id, advanced_info['Title'] + '\n\n\nTrailer: ' + trailer + '\n\n\n' + \
                        stringify_advanced_movie_info(advanced_info), reply_markup = action_reply_markup_extremely_reduced)

    advanced_info['Trailer'] = trailer

    write_to_redis(redis_key, advanced_info, True)

def send_movie_info(bot, chat_id):

    try:
        movie = users[chat_id].movies[users[chat_id].indexes[users[chat_id].tracker][users[chat_id].genre]]
    except IndexError:
        bot.sendMessage(chat_id, 'There are no more movies')
        return

    cached_movie_info = get_from_redis(movie.title)

    if cached_movie_info is not None:
        print(cached_movie_info)
        if cached_movie_info['Poster'] is not None:
            bot.sendPhoto(chat_id, cached_movie_info['Poster'])
        users[chat_id].imdb_id = cached_movie_info.get('imdbID')
        users[chat_id].current_title = movie.title

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

    if users[chat_id].tracker == 'act':
        advanced_info['Schedule'] = save_movie_today_schedule(advanced_info['Title'])
    if users[chat_id].tracker == 'yup' or users[chat_id].tracker == 'mine' or users[chat_id].tracker == 'act':
        href = movie.href
    elif users[chat_id].tracker == 'pbay':
        href = pa.url + movie.href

    if advanced_info['Response'] == 'False':
        send_standart_movie_info(bot, chat_id, movie.title, href)
    else:
        send_advanced_movie_info(bot, chat_id, advanced_info, movie.title, href)

def send_first_movie_msg(bot, chat_id, tracker):
    if tracker == 'pbay' or tracker == 'mine':
        genre = 'any'
        users[chat_id].genre = genre
        users[chat_id].state = states['iterating']
        print('Yohoho')

        if users[chat_id].indexes[users[chat_id].tracker].get(genre) is None:
            users[chat_id].indexes[users[chat_id].tracker][genre] = 0
            users[chat_id].pages[users[chat_id].tracker][genre] = 1
        else:
            increase_index(chat_id)

        update_movies(chat_id)

        send_movie_info(bot, chat_id)
#
#other needed methods
#

def update_movies(chat_id):

    user = users[chat_id]

    tracker = user.tracker
    genre = user.genre
    page = user.pages[tracker][genre]

    redis_key = str(tracker) + delimiter + str(genre) + delimiter + str(page)
    print('iop')
    cached_movies = get_from_redis(redis_key)
    print('iop')
    if cached_movies is not None:
        users[chat_id].movies = cached_movies
        return

    if tracker == 'yup':
        movies = ya.get_movies_by_genre(genre, page)
    elif tracker == 'pbay':
        movies = pa.get_movies_by_page(page)
    elif tracker == 'mine':
        movies = get_top_movies(top_movies_xml_path)
    elif tracker == 'act':
        movies = kudago_adapter.get_filtered_actual_movies(genre)
    print('iop')
    write_to_redis(redis_key, movies, True)
    print('iop')
    users[chat_id].movies = movies

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
        movies = kudago_adapter.get_actual_movies(genre)
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
        movies = kudago_adapter.get_actual_movies(genre)

    return movies
    #write_to_redis(redis_key, movies, True)

def increase_index(chat_id):

    user = users[chat_id]

    tracker = user.tracker
    genre = user.genre

    if user.indexes[tracker][genre] < len(user.movies) - 1:
        users[chat_id].indexes[tracker][genre] += 1
    else:
        users[chat_id].indexes[tracker][genre] = 0
        users[chat_id].pages[tracker][genre] += 1
        update_movies(chat_id)
