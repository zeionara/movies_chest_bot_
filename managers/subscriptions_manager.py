import time

from constants import genred_trackers, delimiter, any_keyword, first_page, trackers, genres_lower, delay_between_request_sequence

from shared import subscribed_to, users

from movies_manager import cache_page

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

            #--cache_page(tracker, any_keyword, first_page)
            #--time.sleep(delay_between_request_sequence)
        else:
            for genre in selected_genres:
                redis_key = tracker + delimiter + genre + delimiter + str(first_page)
                redis_keys.append(redis_key)

                if redis_key not in subscribed_to:
                    subscribed_to[redis_key] = [chat_id]
                else:
                    subscribed_to[redis_key].append(chat_id)
                    subscribed_to[redis_key] = list(set(subscribed_to[redis_key]))

                #--cache_page(tracker, genre, first_page)
                #--time.sleep(delay_between_request_sequence)


    #users[chat_id].subscription_keys = redis_keys

    #for redis_key in redis_keys:
    #    if redis_key not in subscribed_to:
    #        subscribed_to.append(redis_key)

    print(subscribed_to)
