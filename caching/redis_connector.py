#
#python
#

import datetime
import redis
import pickle
from collections import namedtuple

#
#resources
#

from constants import redis_key_delimiter, time_prefix, creation_time_prefix, redis_host, redis_port

redis_connection = redis.StrictRedis(host = redis_host, port = redis_port, db=0)

Movie = namedtuple('Movie','title poster description trailer')
MovieHeader = namedtuple('MovieHeader','title href')
MovieExtendedHeader = namedtuple('MovieExtendedHeader','title href id original_title')

#
#converts key to valid string representation
#

def stringify_key(key):
    str_key = str(key)
    if (str_key[:2] == "b'"):
        str_key = str_key[2:-1]
    return str_key

#
#writes pickled value to redis by key, updates access time and creation time (if necessary)
#

def write_to_redis(key, value, write_creation_time):
    global redis_connection

    str_key = stringify_key(key)
    redis_connection.set(str_key, pickle.dumps(value))
    redis_connection.set(time_prefix + redis_key_delimiter + str_key, pickle.dumps(datetime.datetime.now()))

    if write_creation_time:
        redis_connection.set(creation_time_prefix + redis_key_delimiter + str_key, pickle.dumps(datetime.datetime.now()))

#
#updates access time for specific key
#

def update_redis_time(key):
    global redis_connection

    str_key = stringify_key(key)
    redis_connection.set(time_prefix + redis_key_delimiter + str_key, pickle.dumps(datetime.datetime.now()))

#
#gets unpickled value from redis by key and returns it, updates last access time also
#

def get_from_redis(key):
    packed_object = redis_connection.get(key)
    if packed_object is not None:
        update_redis_time(key)
        res = pickle.loads(packed_object)
        return res
    return None

#
#checks is there actual entry in the cache for a movie id
#

def is_there_valid_schedule(id):
    if get_from_redis('schedule' + redis_key_delimiter + str(id)) is None:
        return False
    return True
