#from shared import users
import logging

from user import get_user, create_user
from db_connection_manager import get_session

from shared import ya, pa

from redis_connector import get_from_redis, write_to_redis

from constants import delimiter, reviews_prefix

from keyboard_markups import action_reply_markup_review_imdb, action_reply_markup_review_kp, action_reply_markup_review_kp_extended,\
    action_reply_markup_review_rtc, action_reply_markup_review_rtc_extended, action_reply_markup_review_rta, action_reply_markup_review_rta_extended

from string_converting import chunkstring

from message_manager import send_chunked_forked

import imdb_adapter
import kinopoisk_adapter
import rotten_tomatoes_adapter

#
#get movie id for reviews depending on provider
#

def get_movie_id(user, provider):
    if provider == 'imdb':
        return user.imdb_id
    elif provider == 'kp' or provider == 'rt':
        return user.current_title

#
#get review list identifier depending on provider and movie id
#

def get_movie_review_list_index(provider, id):
    index = str(provider) + delimiter + str(id)
    return index

#
#update review list inside user's stored entry
#

def update_reviews(chat_id):
    user = get_user(chat_id)
    session = get_session()

    provider = user.reviews_provider
    reviews_group = user.reviews_group

    id = get_movie_id(user, provider)
    index = get_movie_review_list_index(provider, id)

    logging.info(index)

    #if there might be several pages of reviews, get valid current page number

    if user.review_pages.get(index) is not None:
        page = user.review_pages[index].get(reviews_group)
        if page is None:
            user.review_pages[index][reviews_group] = 1
            page = 1

    redis_key = str(reviews_prefix) + delimiter + str(provider) + delimiter + str(id)

    #get reviews from cache if it is possible

    cached_reviews = get_from_redis(redis_key)

    logging.info('cached reviews : {}'.format(cached_reviews))

    if cached_reviews is not None and len(cached_reviews) != 0:
        user.reviews = cached_reviews
        session.flush()
        return

    #otherwise get from external source and cache it

    logging.info('selecting')

    if provider == 'imdb':
        logging.info('getting from site for ')
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

#
#move review pointer to the next entry (only for review lists with multiple pages)
#

def increase_reviews_index(chat_id):
    user = get_user(chat_id)
    session = get_session()

    reviews_group = user.reviews_group
    provider = user.reviews_provider

    index = get_movie_review_list_index(provider, get_movie_id(user, provider))

    if user.review_indexes[index][reviews_group] < len(user.reviews) - 1:
        user.review_indexes[index][reviews_group] += 1
    else:
        user.review_indexes[index][reviews_group] = 0
        user.review_pages[index][reviews_group] += 1
        update_reviews(chat_id)

    session.flush()

#
#get text of the current review
#

def get_review(user, provider, index, reviews_group):
    logging.info('Reviews in user: {}'.format(user.reviews))
    try:
        if provider == 'rt':
            review = user.reviews[user.review_indexes[index][reviews_group]]
        elif provider == 'kp' or provider == 'imdb':
            review = user.reviews[user.review_indexes[index]]
    except IndexError:
        review = 'There are no more reviews'
    return review

#
#send review text to a user
#

def send_review_info(bot, chat_id):
    user = get_user(chat_id)
    session = get_session()

    provider = user.reviews_provider
    reviews_group = user.reviews_group
    imdb_id = user.imdb_id

    index = get_movie_review_list_index(provider, get_movie_id(user, provider))

    review = get_review(user, provider, index, reviews_group)

    reply_markups = [action_reply_markup_review_imdb, action_reply_markup_review_kp, action_reply_markup_review_kp_extended,
        action_reply_markup_review_rtc, action_reply_markup_review_rtc_extended, action_reply_markup_review_rta,
        action_reply_markup_review_rta_extended]

    conditions = [provider == 'imdb', provider == 'kp' and imdb_id is None, provider == 'kp',
        provider == 'rt' and reviews_group == 'critics' and imdb_id is None, provider == 'rt' and reviews_group == 'critics',
        provider == 'rt' and reviews_group == 'audience' and imdb_id is None, provider == 'rt' and reviews_group == 'audience']

    send_chunked_forked(bot = bot, chat_id = chat_id, message = review, reply_markups = reply_markups, conditions = conditions)

    session.flush()
