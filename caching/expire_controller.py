#
#standard libs
#


import re
import datetime
import redis
import pickle
import time
import sys

#
#project libs
#

#redis keys generation and filtering
from constants import delimiter, redis_key_delimiter, time_prefix, creation_time_prefix, delay_between_notifying_users, delay_between_request_sequence
#redis keys control
from constants import max_lifetime, max_memory, checking_interval
#redis storage
from redis_connector import redis_connection, get_from_redis, write_to_redis

from shared import subscribed_to

from movies_manager import load_page

from subscriptions_manager import notify_all

from actual_movies_filter import save_all_movie_schedules

executing = True

def get_key(key):
    return redis_key_delimiter.join(key.split(redis_key_delimiter)[1:])

def get_movies_for_notification(new_page, old_page):
    result = []
    was_occured_earlier = False
    for new_movie in new_page:
        was_occured_earlier = False
        searched_title_lower = new_movie.title.lower()
        for old_movie in old_page:
            if searched_title_lower == old_movie.title.lower():
                was_occured_earlier = True
                break
        if not was_occured_earlier:
            result.append(new_movie)
    return result

def inspect(arg):

    bot = arg

    current_time = datetime.datetime.now()
    pip = redis_connection.pipeline()
    keys = []

    for key in redis_connection.scan_iter(creation_time_prefix + "*"):
        pip.get(key)
        keys.append(key)

    key_times = pip.execute()
    print('New checking cycle')
    for i in range(len(keys)):

        key_time = pickle.loads(key_times[i])
        key = get_key(str(keys[i])[2:-1])

        print('Key {} exists for {}'.format(str(str.encode(key), 'utf-8'), (current_time - key_time).total_seconds()))

        if ((current_time - key_time).total_seconds() >= max_lifetime):
            print('Expired')
            print(subscribed_to)
            if key in subscribed_to:
                pass
                print('There are users subscribed to this channel! {}'.format(subscribed_to[key]))
                users_for_notification = subscribed_to[key]
                key_parts = key.split(redis_key_delimiter)

                tracker = key_parts[0]
                genre = key_parts[1]
                page = int(key_parts[2])

                new_page = load_page(tracker, genre, page)
                old_page = get_from_redis(key)

                print('Old page')
                print('New page')

                movies_for_notification = get_movies_for_notification(new_page, old_page)
                print(users_for_notification)
                print(movies_for_notification)
                notify_all(bot, users_for_notification, movies_for_notification)

                write_to_redis(key, new_page, True)

                time.sleep(delay_between_request_sequence)
            else:
                redis_connection.delete(key)
                redis_connection.delete(time_prefix + redis_key_delimiter + key)
                redis_connection.delete(str(keys[i])[2:-1])
        else:
            print('Not Expired')

class cached_object_:
     def __init__(self, key, seconds_after_access, size):
         self.key = key
         self.seconds_after_access = seconds_after_access
         self.size = size

def print_cached_objects(cached_objects):
    for cached_object in cached_objects:
        print(cached_object.key," ",cached_object.seconds_after_access," ",cached_object.size)

def inspect_enhanced(arg):
    while(executing):
        save_all_movie_schedules()

        current_time = datetime.datetime.now()
        pip = redis_connection.pipeline()
        pip_entries = redis_connection.pipeline()
        keys = []

        for key in redis_connection.scan_iter(time_prefix + "*"):
            pip.get(key)
            pip_entries.get(get_key(str(key)[2:-1]))
            keys.append(key)

        key_times = pip.execute()
        entries = pip_entries.execute()
        cached_objects = []

        for i in range(len(keys)):
            key_time = pickle.loads(key_times[i])
            key = get_key(str(keys[i])[2:-1])
            cached_objects.append(cached_object_(key, (current_time - key_time).total_seconds(), sys.getsizeof(entries[i])))

        cached_objects.sort(key = lambda cached_object: cached_object.seconds_after_access)

        quantity_to_save = 0
        whole_size = 0

        for cached_object in cached_objects:
            whole_size += cached_object.size
            if (whole_size > max_memory):
                break
            quantity_to_save += 1

        for cached_object in cached_objects[quantity_to_save:]:
            redis_connection.delete(cached_object.key)
            redis_connection.delete(time_prefix + redis_key_delimiter + cached_object.key)

        inspect(arg)
        time.sleep(checking_interval)

#inspect_enhanced((10,))
