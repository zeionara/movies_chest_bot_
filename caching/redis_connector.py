import datetime
import redis
import pickle

from constants import redis_key_delimiter
from constants import time_prefix
from constants import creation_time_prefix
from constants import redis_host
from constants import redis_port

from collections import namedtuple

redis_connection = redis.StrictRedis(host = redis_host, port = redis_port, db=0)

Movie = namedtuple('Movie','title poster description trailer')
MovieHeader = namedtuple('MovieHeader','title href')
MovieExtendedHeader = namedtuple('MovieExtendedHeader','title href id original_title')

def stringify_key(key):
    str_key = str(key)
    if (str_key[:2] == "b'"):
        str_key = str_key[2:-1]
    return str_key

def write_to_redis(key, value, write_creation_time):
    global redis_connection

    str_key = stringify_key(key)
    redis_connection.set(str_key, pickle.dumps(value))
    redis_connection.set(time_prefix + redis_key_delimiter + str_key, pickle.dumps(datetime.datetime.now()))

    if write_creation_time:
        redis_connection.set(creation_time_prefix + redis_key_delimiter + str_key, pickle.dumps(datetime.datetime.now()))

def update_redis_time(key):
    global redis_connection

    str_key = stringify_key(key)
    redis_connection.set(time_prefix + redis_key_delimiter + str_key, pickle.dumps(datetime.datetime.now()))

def get_from_redis(key):
    #print('waiting for redis... ',key)
    packed_object = redis_connection.get(key)
    #print('waiting for redis finished')
    if packed_object is not None:
        #print('>>>>>>')
        update_redis_time(key)
        #print('>>>>>>')
        #print(packed_object)
        res = pickle.loads(packed_object)
        #print('>>>>>>')
        return res
    #print(packed_object)
    return None
