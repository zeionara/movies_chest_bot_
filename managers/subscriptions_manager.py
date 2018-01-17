import time

from constants import genred_trackers, delimiter, any_keyword, first_page, trackers, genres_lower, \
                        tracker_names, delay_between_request_sequence, delay_between_notifying_users

from shared import subscribed_to

from user import get_user, create_user
from db_connection_manager import get_session

from movies_manager import cache_page, get_advanced_movie_info_by_title, send_advanced_single_movie_info

def register_subscription(chat_id, selected_trackers, selected_genres):
    redis_keys = []
    excess_keys = []

    for redis_key in subscribed_to:
        subscribed_to[redis_key].remove(chat_id)
        if len(subscribed_to[redis_key]) == 0:
            excess_keys.append(redis_key)

    for redis_key in excess_keys:
        subscribed_to.pop(redis_key, None)

    for tracker in selected_trackers:
        if tracker not in genred_trackers:
            redis_key = tracker + delimiter + any_keyword + delimiter + str(first_page)
            redis_keys.append(redis_key)

            if redis_key not in subscribed_to:
                subscribed_to[redis_key] = [chat_id]
            else:
                subscribed_to[redis_key].append(chat_id)
                subscribed_to[redis_key] = list(set(subscribed_to[redis_key]))

            cache_page(tracker, any_keyword, first_page)
            time.sleep(delay_between_request_sequence)
        else:
            for genre in selected_genres:
                redis_key = tracker + delimiter + genre + delimiter + str(first_page)
                redis_keys.append(redis_key)

                if redis_key not in subscribed_to:
                    subscribed_to[redis_key] = [chat_id]
                else:
                    subscribed_to[redis_key].append(chat_id)
                    subscribed_to[redis_key] = list(set(subscribed_to[redis_key]))

                cache_page(tracker, genre, first_page)
                print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                print(subscribed_to)
                time.sleep(delay_between_request_sequence)


def unregister_subscription(chat_id, selected_trackers, selected_genres):
    excess_keys = []

    for tracker in selected_trackers:
        if tracker not in genred_trackers:
            redis_key = tracker + delimiter + any_keyword + delimiter + str(first_page)

            if redis_key in subscribed_to:
                subscribed_to[redis_key].remove(chat_id)
                if len(subscribed_to[redis_key]) == 0:
                    excess_keys.append(redis_key)
        else:
            for genre in selected_genres:
                redis_key = tracker + delimiter + genre + delimiter + str(first_page)

                if redis_key in subscribed_to:
                    subscribed_to[redis_key].remove(chat_id)
                    if len(subscribed_to[redis_key]) == 0:
                        excess_keys.append(redis_key)

        for redis_key in excess_keys:
            subscribed_to.pop(redis_key, None)

    print(subscribed_to)

def notify_all(bot, users, movies):
    for chat_id in users:
        for movie in movies:
            movie_info = get_advanced_movie_info_by_title(movie.title)
            movie_info['Href'] = movie.href
            send_advanced_single_movie_info(bot, chat_id, movie_info)
            time.sleep(delay_between_notifying_users)

def get_subscribed_params(chat_id, param_index = 0):
    print('get params')
    result = []
    print(subscribed_to)
    for key in subscribed_to:
        if chat_id in subscribed_to[key]:
            print(key.split(delimiter)[param_index])
            if key.split(delimiter)[param_index] != any_keyword:
                result.append(key.split(delimiter)[param_index])
    print(result)
    return list(set(result))

def get_subscribed_tracker_names(chat_id):
    print('getting locla trackers')
    sub_trackers = get_subscribed_params(chat_id, 0)
    print(sub_trackers)
    sub_tracker_names = []
    for tracker in sub_trackers:
        print(tracker)
        if tracker in trackers:
            sub_tracker_names.append(tracker_names[trackers.index(tracker)])
    return sub_tracker_names

def get_subscribed_genres(chat_id):
    return get_subscribed_params(chat_id, 1)
