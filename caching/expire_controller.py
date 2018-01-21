#
#python
#

import re
import datetime
import redis
import pickle
import time
import sys
import traceback
import logging

#
#odm
#

from subscriptions import get_subscription, get_all_subscriptions

#
#resources
#

from constants import delimiter, redis_key_delimiter, time_prefix, creation_time_prefix, delay_between_notifying_users,\
    delay_between_request_sequence, max_lifetime, max_memory, checking_interval

#
#managers
#

from movies_manager import load_page
from subscriptions_manager import notify_all
from db_connection_manager import get_session

#
#caching
#

from redis_connector import redis_connection, get_from_redis, write_to_redis

executing = True
session = get_session()

class cached_object_:
     def __init__(self, key, seconds_after_access, size):
         self.key = key
         self.seconds_after_access = seconds_after_access
         self.size = size

def print_cached_objects(cached_objects):
    for cached_object in cached_objects:
        print(cached_object.key," ",cached_object.seconds_after_access," ",cached_object.size)

#
#removes prefix of the given key
#

def get_key(key):
    return redis_key_delimiter.join(key.split(redis_key_delimiter)[1:])

#
#returns list of movies which are not found in the cached page, but which are now in external source
#

def get_movies_for_notification(new_page, old_page):
    result = []

    if old_page is None:
        return result

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

#
#returns keys with creation time prefix (in field keys) and assigned values (in field key_times)
#

def get_key_creation_times():
    pip = redis_connection.pipeline()
    keys = []

    for key in redis_connection.scan_iter(creation_time_prefix + "*"):
        pip.get(key)
        keys.append(key)

    key_times = pip.execute()

    return {'keys' : keys, 'key_times' : key_times}

#
#replaces cached entry with a new one and notifies all subscribed users
#

def handle_key_with_bad_creation_time(bot, key, raw_key):
    subscription = get_subscription(key)
    if subscription is not None:
        users_for_notification = subscription.users_ids
        key_parts = key.split(redis_key_delimiter)

        tracker = key_parts[0]
        genre = key_parts[1]
        page = int(key_parts[2])

        new_page = load_page(tracker, genre, page)
        old_page = get_from_redis(key)

        notify_all(bot, users_for_notification, get_movies_for_notification(new_page, old_page), session)

        write_to_redis(key, new_page, True)

        time.sleep(delay_between_request_sequence)
    else:
        redis_connection.delete(key)
        redis_connection.delete(time_prefix + redis_key_delimiter + key)
        redis_connection.delete(str(raw_key)[2:-1])

#
#analyzes keys having creation time prefix, updates entries in the caches and notifies subscribed users
#

def inspect(bot):
    try:
        key_creation_times = get_key_creation_times()
        keys = key_creation_times.get('keys')
        key_times = key_creation_times.get('key_times')

        for i in range(len(keys)):
            key_time = pickle.loads(key_times[i])
            key = get_key(str(keys[i])[2:-1])
            print('key : ',key)
            current_time = datetime.datetime.now()

            if ((current_time - key_time).total_seconds() >= max_lifetime):
                print('exceeded')
                handle_key_with_bad_creation_time(bot, key, keys[i])
    except Exception:
        print(sys.exc_info()[1])
        print(traceback.print_tb(sys.exc_info()[2]))

#
#returns cached entries having time of the last access in the cache
#

def get_cached_objects():
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

    return cached_objects

#
#analyzes entries having key with time prefix and deletes the oldest if necessary
#

def inspect_enhanced(arg):
    while(executing):
        print('excecuting cycle')

        cached_objects = get_cached_objects()

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
