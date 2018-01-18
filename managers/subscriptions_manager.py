import time

from constants import genred_trackers, delimiter, any_keyword, first_page, trackers, genres_lower, \
                        tracker_names, delay_between_request_sequence, delay_between_notifying_users

from subscriptions import create_subscription, get_subscription, get_all_subscriptions, remove_subscription, extend_subscription, reduce_subscription,\
    reduce_subscriptions

from movies_manager import cache_page, get_advanced_movie_info_by_title, send_advanced_single_movie_info

#
#add user's chat_id to the entry of subscription page
#

def handle_subscribed_page(tracker, genre, page, chat_id):
    redis_key = tracker + delimiter + genre + delimiter + str(page)

    extend_subscription(redis_key, chat_id)

    cache_page(tracker, genre, page)
    time.sleep(delay_between_request_sequence)

#
#delete user's chat_id from the list of the subscription page, and if they were last, delete appropriate document from the collection
#

def handle_unsubscribed_page(tracker, genre, page, chat_id):
    redis_key = tracker + delimiter + any_keyword + delimiter + str(page)
    reduce_subscription(redis_key, chat_id)

#
#subscribe user to the selected channels
#

def register_subscription(chat_id, selected_trackers, selected_genres):
    reduce_subscriptions(chat_id)

    for tracker in selected_trackers:
        if tracker not in genred_trackers:
            handle_subscribed_page(tracker = tracker, genre = any_keyword, page = first_page, chat_id = chat_id)
        else:
            for genre in selected_genres:
                handle_subscribed_page(tracker = tracker, genre = genre, page = first_page, chat_id = chat_id)

#
#unsubscribe user from the selected channels
#

def unregister_subscription(chat_id, selected_trackers, selected_genres):
    for tracker in selected_trackers:
        if tracker not in genred_trackers:
            handle_unsubscribed_page(tracker = tracker, genre = any_keyword, page = first_page, chat_id = chat_id)
        else:
            for genre in selected_genres:
                handle_unsubscribed_page(tracker = tracker, genre = genre, page = first_page, chat_id = chat_id)

#
#send information about all movies from the list to all users
#

def notify_all(bot, users, movies):
    for chat_id in users:
        for movie in movies:
            movie_info = get_advanced_movie_info_by_title(movie.title)
            movie_info['Href'] = movie.href
            send_advanced_single_movie_info(bot, chat_id, movie_info)
            time.sleep(delay_between_notifying_users)

#
#get list of certain parts of keys of pages which the given user is subscribed to
#

def get_subscribed_params(chat_id, param_index = 0):
    result = []
    for subscription in get_all_subscriptions():
        if chat_id in subscription.users_ids:
            key = subscription.page_key
            if key.split(delimiter)[param_index] != any_keyword:
                result.append(key.split(delimiter)[param_index])
    return list(set(result))

#
#get list of tracker names which the given user is subscribed to
#

def get_subscribed_tracker_names(chat_id):
    sub_trackers = get_subscribed_params(chat_id = chat_id, param_index = 0)
    sub_tracker_names = []
    for tracker in sub_trackers:
        if tracker in trackers:
            sub_tracker_names.append(tracker_names[trackers.index(tracker)])
    return sub_tracker_names

#
#get list of genres which the given user is subscribed to
#

def get_subscribed_genres(chat_id):
    return get_subscribed_params(chat_id = chat_id, param_index = 1)
