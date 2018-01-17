#from shared import users
from user import get_user, create_user
from db_connection_manager import get_session

from shared import ya
from shared import pa

from redis_connector import get_from_redis
from redis_connector import write_to_redis

from constants import delimiter
from constants import reviews_prefix

from keyboard_markups import action_reply_markup_review_imdb
from keyboard_markups import action_reply_markup_review_kp
from keyboard_markups import action_reply_markup_review_kp_extended
from keyboard_markups import action_reply_markup_review_rtc
from keyboard_markups import action_reply_markup_review_rtc_extended
from keyboard_markups import action_reply_markup_review_rta
from keyboard_markups import action_reply_markup_review_rta_extended

from string_converting import chunkstring

import imdb_adapter
import kinopoisk_adapter
import rotten_tomatoes_adapter

def get_movie_id(chat_id):
    user = get_user(chat_id)
    session = get_session()

    #user = users[chat_id]
    provider = user.reviews_provider

    if provider == 'imdb':
        return user.imdb_id
    elif provider == 'kp' or provider == 'rt':
        return user.current_title

def get_movie_review_list_index(provider, id):
    index = str(provider) + delimiter + str(id)
    return index

def update_reviews(chat_id):
    user = get_user(chat_id)
    session = get_session()

    provider = user.reviews_provider
    reviews_group = user.reviews_group

    id = get_movie_id(chat_id)
    index = get_movie_review_list_index(provider, id)

    if user.review_pages.get(index) is not None:
        page = user.review_pages[index].get(reviews_group)
        if page is None:
            user.review_pages[index][reviews_group] = 1
            page = 1

    redis_key = str(reviews_prefix) + delimiter + str(provider) + delimiter + str(id)

    cached_reviews = get_from_redis(redis_key)

    if cached_reviews is not None:
        user.reviews = cached_reviews
        session.flush()
        return

    if provider == 'imdb':
        reviews = imdb_adapter.get_reviews(str(id))
    elif provider == 'kp':
        reviews = kinopoisk_adapter.get_reviews(str(id))
    elif provider == 'rt' and reviews_group == 'critics':
        reviews = rotten_tomatoes_adapter.get_reviews(str(id), critics = True, page = page)
    elif provider == 'rt' and reviews_group == 'audience':
        reviews = rotten_tomatoes_adapter.get_reviews(str(id), critics = False, page = page)

    write_to_redis(redis_key, reviews, True)
    user.reviews = reviews

    session.flush()

def increase_reviews_index(chat_id):
    user = get_user(chat_id)
    session = get_session()

    reviews_group = user.reviews_group
    provider = user.reviews_provider

    id = get_movie_id(chat_id)
    index = get_movie_review_list_index(provider, id)

    if user.review_indexes[index][reviews_group] < len(user.reviews) - 1:
        user.review_indexes[index][reviews_group] += 1
    else:
        user.review_indexes[index][reviews_group] = 0
        user.review_pages[index][reviews_group] += 1
        update_reviews(chat_id)

    session.flush()

def send_review_info(bot, chat_id):
    user = get_user(chat_id)
    session = get_session()
    #user = users[chat_id]

    provider = user.reviews_provider
    reviews_group = user.reviews_group
    imdb_id = user.imdb_id

    id = get_movie_id(chat_id)
    index = get_movie_review_list_index(provider, id)

    try:
        if provider == 'rt':
            review = user.reviews[user.review_indexes[index][reviews_group]]
        elif provider == 'kp' or provider == 'imdb':
            review = user.reviews[user.review_indexes[index]]
    except IndexError:
        review = 'There are no more reviews'

    chunks = chunkstring(review)
    for chunk in chunks[:-1]:
        bot.sendMessage(chat_id, chunk)

    if provider == 'imdb':
        reply_markup = action_reply_markup_review_imdb
    elif provider == 'kp' and imdb_id is None:
        reply_markup = action_reply_markup_review_kp
    elif provider == 'kp':
        reply_markup = action_reply_markup_review_kp_extended
    elif provider == 'rt' and reviews_group == 'critics' and imdb_id is None:
        reply_markup = action_reply_markup_review_rtc
    elif provider == 'rt' and reviews_group == 'critics':
        reply_markup = action_reply_markup_review_rtc_extended
    elif provider == 'rt' and reviews_group == 'audience' and imdb_id is None:
        reply_markup = action_reply_markup_review_rta
    elif provider == 'rt' and reviews_group == 'audience':
        reply_markup = action_reply_markup_review_rta_extended

    bot.sendMessage(chat_id, chunks[-1], reply_markup = reply_markup)
    session.flush()
