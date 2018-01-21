#
#python
#

import logging

#
#odm
#

from user import get_user

#
#resources
#

from keyboard_markups import action_reply_markup
from constants import msg_tracker_is_not_set, msg_genre_is_not_set, msg_imdb_id_is_not_set, msg_kp_id_is_not_set
from constants import action_back_to_the_beginning, action_show_next, action_show_reviews_from_imdb, action_show_reviews_from_kinopoisk,\
    action_show_critics_reviews_from_rotten_tomatoes, action_show_audience_reviews_from_rotten_tomatoes, action_return_from_reviews_to_movies,\
    action_show_info_from_wiki
from constants import rotten_tomatoes_reviews_provider, imdb_reviews_provider, kinopoisk_reviews_provider

#
#managers
#

from db_connection_manager import get_session
from reviews_manager import get_movie_id, get_movie_review_list_index, update_reviews, send_review_info, increase_reviews_index
from movies_manager import increase_index, send_movie_info, update_movies
from message_manager import send_plain
from wiki_manager import send_wiki_info

#
#handles moving to the next review or movie
#

def handle_action_show_next(user, session, provider, index, searching_movies):
    if searching_movies:
        increase_index(user, session)
    else:
        if provider == rotten_tomatoes_reviews_provider:
            increase_reviews_index(user, session, provider, index)
        elif provider == imdb_reviews_provider or provider == kinopoisk_reviews_provider:
            user.review_indexes[index] += 1
            session.flush()

#
#handles moving to the beginning of reviews or movies list
#

def handle_action_back_to_the_beginning(user, session, provider, index, searching_movies):
    tracker = user.tracker
    genre = user.genre

    if searching_movies and user.pages[tracker][genre] == 1:
        user.indexes[tracker][genre] = 0
    elif searching_movies:
        user.pages[tracker][genre] = 1
        user.indexes[tracker][genre] = 0
        update_movies(user, session)
    else: # if searching for reviews
        if provider == 'rt':
            reviews_group = user.reviews_group
            if user.review_pages[index][reviews_group] == 1:
                user.review_indexes[index][reviews_group] = 0
            else:
                user.review_pages[index][reviews_group] = 1
                user.review_indexes[index][reviews_group] = 0
                update_reviews(user, session)
        elif provider == 'kp' or provider == 'imdb':
            user.review_indexes[index] = 0

    session.flush()

#
#handles switching to reading movie's reviews from imdb
#

def handle_action_show_reviews_from_imdb(user, session):
    if user.imdb_id is None:
        send_plain(bot = bot, chat_id = chat_id, message = msg_imdb_id_is_not_set)
        return

    provider = imdb_reviews_provider
    user.reviews_provider = provider

    id = user.imdb_id
    index = get_movie_review_list_index(provider, id)

    user.searching_movies = False

    update_reviews(user, session)

    if user.review_indexes.get(index) is None:
        user.review_indexes[index] = 0
    else:
        user.review_indexes[index] += 1

    session.flush()

#
#handles switching to reading movie's reviews from kinopoisk
#

def handle_action_show_reviews_from_kinopoisk(user, session):
    if user.current_title is None:
        send_plain(bot = bot, chat_id = chat_id, message = msg_kp_id_is_not_set)
        return

    provider = kinopoisk_reviews_provider

    user.reviews_provider = provider

    id = user.current_title
    index = get_movie_review_list_index(provider, id)

    user.searching_movies = False

    update_reviews(user, session)

    if user.review_indexes.get(index) is None:
        user.review_indexes[index] = 0
    else:
        user.review_indexes[index] += 1

    session.flush()

#
#handles switching to reading movie's reviews from rotten tomatoes
#

def handle_action_show_reviews_from_rotten_tomatoes(user, session, action):
    if action == action_show_critics_reviews_from_rotten_tomatoes:
        user.reviews_group = 'critics'
    else:
        user.reviews_group = 'audience'

    provider = rotten_tomatoes_reviews_provider
    user.reviews_provider = provider

    id = user.current_title
    index = get_movie_review_list_index(provider, id)
    user.searching_movies = False

    if user.review_pages.get(index) is None:
        user.review_pages[index] = {}

    if user.review_pages[index].get(user.reviews_group) is None:
        user.review_pages[index][user.reviews_group] = 1

    update_reviews(user, session)

    if user.review_indexes.get(index) is None:
        user.review_indexes[index] = {}
    if user.review_indexes[index].get(user.reviews_group) is None:
        user.review_indexes[index][user.reviews_group] = 0
    else:
        increase_reviews_index(user, session, provider, index)

    session.flush()

#
#general method for pre-handling any kind of action and calling specific handler for each one
#

def handle_action(user, session, action, bot):
    chat_id = user.chat_id

    searching_movies = user.searching_movies

    changing_iterating_state = (action == action_show_reviews_from_imdb) or (action == action_show_reviews_from_kinopoisk) or\
        (action == action_show_critics_reviews_from_rotten_tomatoes) or (action == action_show_audience_reviews_from_rotten_tomatoes) or\
        (action == action_show_info_from_wiki)

    if searching_movies and not changing_iterating_state:
        if user is None:
            send_plain(bot = bot, chat_id = chat_id, message = msg_tracker_is_not_set)
            return
        elif user.genre is None:
            send_plain(bot = bot, chat_id = chat_id, message = msg_genre_is_not_set)
            return
        tracker = user.tracker
        genre = user.genre

    provider = user.reviews_provider

    id = get_movie_id(user, provider)
    index = get_movie_review_list_index(provider, id)

    if action == action_back_to_the_beginning:
        handle_action_back_to_the_beginning(user, session, provider, index, searching_movies)
    elif action == action_show_next:
        handle_action_show_next(user, session, provider, index, searching_movies)
    elif action == action_show_reviews_from_imdb:
        handle_action_show_reviews_from_imdb(user, session)
    elif action == action_show_reviews_from_kinopoisk:
        handle_action_show_reviews_from_kinopoisk(user, session)
    elif (action == action_show_critics_reviews_from_rotten_tomatoes or action == action_show_audience_reviews_from_rotten_tomatoes):
        handle_action_show_reviews_from_rotten_tomatoes(user, session, action)
    elif action == action_return_from_reviews_to_movies:
        user.searching_movies = True
        increase_index(user, session)
    elif action == action_show_info_from_wiki:
        send_wiki_info(user, session, user.current_title, bot)
        return

    if user.searching_movies:
        send_movie_info(bot, user, session)
    else:
        send_review_info(bot, user, session)

    session.flush()
