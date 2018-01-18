#from shared import users
import logging

from user import get_user
from db_connection_manager import get_session

from keyboard_markups import action_reply_markup

from constants import msg_tracker_is_not_set
from constants import msg_genre_is_not_set

from reviews_manager import get_movie_id
from reviews_manager import get_movie_review_list_index
from reviews_manager import update_reviews, send_review_info

from movies_manager import increase_index, send_movie_info, update_movies

from reviews_manager import increase_reviews_index

from wiki_manager import send_wiki_info

def handle_next_action(chat_id, provider, index, searching_movies):
    user = get_user(chat_id)
    session = get_session()

    if searching_movies:
        increase_index(chat_id)
    else:
        if provider == 'rt':
            increase_reviews_index(chat_id)
        elif provider == 'imdb' or provider == 'kp':
            user.review_indexes[index] += 1

    session.flush()

def handle_flush_action(chat_id, provider, index, searching_movies):
    user = get_user(chat_id)
    session = get_session()

    tracker = user.tracker
    genre = user.genre

    if searching_movies and user.pages[tracker][genre] == 1:
        user.indexes[tracker][genre] = 0
    elif searching_movies:
        user.pages[tracker][genre] = 1
        update_movies(chat_id)
    else:
        if provider == 'rt':
            user.review_indexes[index][user.reviews_group] = 0
        elif provider == 'kp' or provider == 'imdb':
            user.review_indexes[index] = 0

    session.flush()

def handle_imdbrev_action(chat_id):
    logging.info('IMDB Rev upd')
    user = get_user(chat_id)
    session = get_session()

    logging.info('IMDB Rev upd')
    if user.imdb_id is not None:
        provider = 'imdb'
        user.reviews_provider = provider
        logging.info('IMDB Rev upd')
        id = user.imdb_id
        index = get_movie_review_list_index(provider, id)
        user.searching_movies = False
        logging.info('IMDB Rev upd')
        update_reviews(chat_id)
        logging.info('IMDB Rev upd after')

        if user.review_indexes.get(index) is None:
            user.review_indexes[index] = 0
        else:
            user.review_indexes[index] += 1

    session.flush()

def handle_kprev_action(chat_id):
    user = get_user(chat_id)
    session = get_session()

    provider = 'kp'
    user.reviews_provider = provider

    id = user.current_title
    index = get_movie_review_list_index(provider, id)
    user.searching_movies = False

    update_reviews(chat_id)

    if user.review_indexes.get(index) is None:
        user.review_indexes[index] = 0
    else:
        print(user.review_indexes)
        print(index)
        user.review_indexes[index] += 1

    session.flush()

def handle_rtrev_action(chat_id, action):
    user = get_user(chat_id)
    session = get_session()

    if action == 'rtcrev':
        user.reviews_group = 'critics'
    else:
        user.reviews_group = 'audience'

    provider = 'rt'
    user.reviews_provider = provider

    id = user.current_title
    index = get_movie_review_list_index(provider, id)
    user.searching_movies = False

    if user.review_pages.get(index) is None:
        page = user.review_pages[index] = {}
    if user.review_pages[index].get(user.reviews_group) is None:
        user.review_pages[index][user.reviews_group] = 1

    update_reviews(chat_id)

    if user.review_indexes.get(index) is None:
        user.review_indexes[index] = {}
    if user.review_indexes[index].get(user.reviews_group) is None:
        user.review_indexes[index][user.reviews_group] = 0
    else:
        increase_reviews_index(chat_id)

    session.flush()

def handle_action(chat_id, action, bot):
    user = get_user(chat_id)
    session = get_session()

    searching_movies = user.searching_movies

    changing_iterating_state = action == 'imdbrev' or action == 'kprev' or action == 'rtcrev' or action == 'rtarev' or action == 'wiki'

    if user is None and searching_movies and not changing_iterating_state:
        bot.sendMessage(chat_id = chat_id, text = msg_tracker_is_not_set)
        return
    elif user.genre is None and searching_movies and not changing_iterating_state:
        bot.sendMessage(chat_id = chat_id, text = msg_genre_is_not_set)
        return

    if searching_movies and not changing_iterating_state:
        tracker = user.tracker
        genre = user.genre

    provider = user.reviews_provider

    id = get_movie_id(user, provider)
    index = get_movie_review_list_index(provider, id)

    if action == 'flush':
        handle_flush_action(chat_id, provider, index, searching_movies)
    elif action == 'next':
        handle_next_action(chat_id, provider, index, searching_movies)
    elif action == 'imdbrev':
        handle_imdbrev_action(chat_id)
    elif action == 'kprev':
        handle_kprev_action(chat_id)
    elif (action == 'rtcrev' or action == 'rtarev'):
        handle_rtrev_action(chat_id, action)
    elif action == 'imdbrevexit':
        user.searching_movies = True
        increase_index(chat_id)
    elif action == 'wiki':
        send_wiki_info(bot, chat_id, user.current_title)
        return

    if user.searching_movies:
        send_movie_info(bot, chat_id)
    else:
        send_review_info(bot, chat_id)

    session.flush()
