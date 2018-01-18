import sys
sys.path.append('../managers/')

from db_connection_manager import get_session

from ming import schema
from ming.odm import FieldProperty
from ming.odm.declarative import MappedClass
from ming.odm.mapper import MapperExtension

collection_name = 'subscriptions'

session = get_session()

class Subscription(MappedClass):
    class __mongometa__:
        session = session
        name = collection_name

    _id = FieldProperty(schema.ObjectId)

    page_key = FieldProperty(schema.String(required = True))
    users_ids = FieldProperty(schema.Array(schema.Int))

def create_subscription(page_key, users_ids = []):
    subscription = Subscription(page_key = page_key, users_ids = users_ids)
    session.flush()
    return subscription

def get_subscription(page_key):
    return Subscription.query.get(page_key = page_key)

def get_all_subscriptions():
    return Subscription.query.find().all()

def remove_subscription(page_key):
    Subscription.query.remove({'page_key' : page_key})
    session.flush()

def extend_subscription(redis_key, chat_id):
    subscription = get_subscription(redis_key)

    if subscription is None:
        create_subscription(redis_key, [chat_id])
    else:
        subscription.users_ids.append(chat_id)
        subscription.users_ids = list(set(subscription.users_ids))

    session.flush()

def cut_subscription(subscription, chat_id):
    if chat_id in subscription.users_ids:
        subscription.users_ids.remove(chat_id)

    if len(subscription.users_ids) == 0:
        remove_subscription(redis_key)

def reduce_subscriptions(chat_id):
    excess_keys = []

    for subscription in get_all_subscriptions():
        redis_key = subscription.page_key

        cut_subscription(subscription = subscription, chat_id = chat_id)

    for redis_key in excess_keys:
        remove_subscription(redis_key)

    session.flush()

def reduce_subscription(redis_key, chat_id):
    subscription = get_subscription(redis_key)
    if subscription is not None:

        cut_subscription(subscription = subscription, chat_id = chat_id)

    session.flush()

#print(get_all_subscriptions())
