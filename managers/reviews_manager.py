from main import users
from main import ya
from main import pa

from redis_connector import get_from_redis

from constants import delimiter

from keyboard_markups import action_reply_markup_review_imdb
from keyboard_markups import action_reply_markup_review_kp
from keyboard_markups import action_reply_markup_review_kp_extended
from keyboard_markups import action_reply_markup_review_rtc
from keyboard_markups import action_reply_markup_review_rtc_extended
from keyboard_markups import action_reply_markup_review_rta
from keyboard_markups import action_reply_markup_review_rta_extended

from string_converting import chunkstring

def get_movie_id(chat_id):

    user = users[chat_id]
    provider = user.reviews_provider

    if provider == 'imdb':
        return user.imdb_id
    elif provider == 'kp' or provider == 'rt':
        return user.current_title

def get_movie_review_list_index(provider, id):
    index = str(provider) + delimiter + str(id)

def update_reviews(chat_id):

    provider = users[chat_id].reviews_provider
    reviews_group = users[chat_id].reviews_group

    id = get_movie_id(chat_id)
    index = get_movie_review_list_index(provider, id)

    if users[chat_id].review_pages.get(index) is not None:
        page = users[chat_id].review_pages[index].get(reviews_group)
        if page is None:
            users[chat_id].review_pages[index].get(reviews_group) = 1
            page = 1

    redis_key = str(reviews_prefix) + delimiter + str(provider) + delimiter + str(id)

    cached_reviews = get_from_redis(redis_key)

    if cached_reviews is not None:
        users[chat_id].reviews = cached_reviews
        return

    if provider == 'imdb':
        reviews = imdb.get_reviews(str(id))
    elif provider == 'kp':
        reviews = kinopoisk_.get_reviews(str(id))
    elif provider == 'rt' and reviews_group == 'critics':
        reviews = rotten_tomatoes.get_reviews(str(id), critics = True, page = page)
    elif provider == 'rt' and reviews_group == 'audience':
        reviews = rotten_tomatoes.get_reviews(str(id), critics = False, page = page)

    write_to_redis(redis_key, reviews, True)
    users[chat_id].reviews = reviews

def increase_reviews_index(chat_id):

    reviews_group = users[chat_id].reviews_group
    provider = users[chat_id].reviews_provider

    id = get_movie_id(chat_id)
    index = get_movie_review_list_index(provider, id)

    if users[chat_id].review_indexes[index][reviews_group] < len(users[chat_id].reviews) - 1:
        users[chat_id].review_indexes[index][reviews_group] += 1
    else:
        users[chat_id].review_indexes[index][reviews_group] = 0
        users[chat_id].review_pages[index][reviews_group] += 1
        update_reviews(chat_id)

def send_review_info(bot, chat_id):

    user = users[chat_id]

    provider = user.reviews_provider
    reviews_group = user.reviews_group
    imdb_id = user.imdb_id

    id = get_movie_id(chat_id)
    index = get_movie_review_list_index(provider, id)

    try:
        if provider == 'rt':
            review = user.reviews[users[chat_id].review_indexes[index][reviews_group]]
        elif provider == 'kp' or provider == 'imdb':
            review = users[chat_id].reviews[users[chat_id].review_indexes[index]]
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
