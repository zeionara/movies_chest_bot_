import sys
sys.path.append('../managers/')

from db_connection_manager import get_session

from ming import schema
from ming.odm import FieldProperty
from ming.odm.declarative import MappedClass
from ming.odm.mapper import MapperExtension

collection_name = 'users'

session = get_session()


class UserExtension(MapperExtension):
    def before_insert(self, obj, st, sess):
        print('before')
        print(obj)

        if obj.indexes is None:
            obj.indexes = {}
        if obj.pages is None:
            obj.pages = {}

        if obj.indexes == {}:
            obj.indexes[obj.tracker] = {}
        if obj.pages == {}:
            obj.pages[obj.tracker] = {}
        print(obj)

    def after_insert(self, obj, st, sess):
        print(obj.pages)

class User(MappedClass):
    class __mongometa__:
        session = session
        name = collection_name
        extensions = [ UserExtension ]

    _id = FieldProperty(schema.ObjectId)

    chat_id = FieldProperty(schema.Int(required = True))

    #self.tracker = tracker
    tracker = FieldProperty(schema.String(required = True))

    state = FieldProperty(schema.Int(required = True))
    #self.indexes = {tracker : {}}
    indexes = FieldProperty(schema.Anything(if_missing = {}))
    #self.pages = {tracker : {}}
    pages = FieldProperty(schema.Anything(if_missing = {}))
    #self.movies = None
    movies = FieldProperty(schema.Anything(if_missing = None))
    #self.reviews = None
    reviews = FieldProperty(schema.Anything(if_missing = None))
    #self.review_indexes = {}
    review_indexes = FieldProperty(schema.Anything(if_missing = {}))
    #self.page = 1
    page = FieldProperty(schema.Int(if_missing = 1))

    #self.genre = None
    genre = FieldProperty(schema.String(if_missing = None))
    #self.category = None
    #self.searching_movies = True
    searching_movies = FieldProperty(schema.Bool(if_missing = True))
    #self.imdb_id = None
    imdb_id = FieldProperty(schema.String(if_missing = None))
    #self.current_title = None
    current_title = FieldProperty(schema.String(if_missing = None))
    #self.reviews_provider = None
    reviews_provider = FieldProperty(schema.String(if_missing = None))
    #self.review_pages = {}
    review_pages = FieldProperty(schema.Object(if_missing = {}))
    #self.reviews_group = None
    reviews_group = FieldProperty(schema.String(if_missing = None))
    #self.wiki_content = None
    wiki_content = FieldProperty(schema.Anything(if_missing = None))
    #self.wiki_keyboard_markup = None
    wiki_keyboard_markup = FieldProperty(schema.Anything(if_missing = None))
    #self.trackers_to_subscribe = None
    trackers_to_subscribe = FieldProperty(schema.Array(schema.String, if_missing = None))

    #self.tmp = None
    tmp = FieldProperty(schema.Anything)

def create_user(chat_id, tracker, state):
    user = User(chat_id = chat_id, tracker = tracker, state = state)
    session.flush()
    return user

def get_user(chat_id):
    return User.query.get(chat_id = chat_id)
