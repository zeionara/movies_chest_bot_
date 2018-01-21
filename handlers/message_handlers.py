#
#python
#

import sys
import traceback
from threading import Thread

#
#odm
#

from user import get_user, create_user

#
#resources
#

from constants import states, tracker_names_delimiter, tracker_names, genres_lower, trackers,\
    msg_choose_genre_to_subscripe, any_keyword, genred_trackers, msg_choose_genre_to_unsubscripe, msg_entered_wrong, msg_subscription_set
from keyboard_markups import yes_no_reply_markup

#
#managers
#

from db_connection_manager import get_session
from movies_manager import send_advanced_single_movie_info, get_advanced_movie_info_by_title
from message_manager import send_plain
from subscriptions_manager import register_subscription, unregister_subscription, get_subscribed_genres

#
#decorators
#

from exception_handling_decorators import print_exceptions

#
#returns tracker names, which were available for selection
#

def get_actual_tracker_names(user_state):
    if user_state == states['choosing_tracker_to_subscribe']:
        return tracker_names
    elif user_state == states['choosing_tracker_to_unsubscribe']:
        return user.tmp

#
#returns genres, which were available for selection
#

def get_actual_genres(user_state):
    if user_state == states['choosing_genre_to_subscribe']:
        return genres_lower
    elif user_state == states['choosing_genre_to_unsubscribe']:
        return user.tmp

#
#converts user's list of tracker names to list of trackers and answer for the question 'Do we need to ask user to select genre?'
#

def handle_users_trackers_list(objs, user_state):
    genred = False

    selected_trackers = []
    selected_tracker_names = [tracker_name.lstrip().rstrip() for tracker_name in objs.split(tracker_names_delimiter)]

    actual_tracker_names = get_actual_tracker_names(user_state)

    if any_keyword in selected_tracker_names:
        selected_tracker_names = []
        for tracker_name in actual_tracker_names:
            selected_trackers.append(trackers[tracker_names.index(tracker_name)])
    else:
        for tracker_name in selected_tracker_names:
            if not (tracker_name in actual_tracker_names):
                send_plain(bot = bot, chat_id = chat_id, message = msg_entered_wrong, reply_markup = yes_no_reply_markup)
                return {}
            if trackers[tracker_names.index(tracker_name)] in genred_trackers:
                genred = True
            selected_trackers.append(trackers[tracker_names.index(tracker_name)])

    return {'selected_trackers' : selected_trackers, 'genred' : genred}

#
#validates user's list of genres
#

def handle_users_genres_list(objs, user_state):
    selected_genres = [genre.lstrip().rstrip() for genre in objs.split(tracker_names_delimiter)]

    actual_genres = get_actual_genres(user.state)

    if any_keyword in selected_genres:
        selected_genres = []
        for genre in actual_genres:
            selected_genres.append(genre)
    else:
        for genre in selected_genres:
            if not (genre in actual_genres):
               send_plain(bot = bot, chat_id = chat_id, message = msg_entered_wrong, reply_markup = yes_no_reply_markup)
               return {}

    return {'selected_genres' : selected_genres}

#
#launches thread for registering/unregistering new subscribtion
#

def start_changing_registering(state, chat_id, trackers_to_subscribe, selected_genres):
    if state == states['choosing_genre_to_subscribe']:
        thread = Thread(target = register_subscription, args = (chat_id, trackers_to_subscribe, selected_genres))
        thread.start()
    elif state == states['choosing_genre_to_unsubscribe']:
        thread = Thread(target = unregister_subscription, args = (chat_id, trackers_to_subscribe, selected_genres))
        thread.start()

#
#sends message to user asking him to select genres for subscribing/unsibscribing
#

def summon_user_to_select_genre(user, bot, chat_id):
    if user.state == states['choosing_genre_to_subscribe']:
        send_plain(bot = bot, chat_id = chat_id, message = msg_choose_genre_to_subscripe + (tracker_names_delimiter+' ').join(genres_lower))
    elif user.state == states['choosing_genre_to_unsubscribe']:
        subscribed_genres = get_subscribed_genres(chat_id)
        user.tmp = subscribed_genres
        send_plain(bot = bot, chat_id = chat_id, message = msg_choose_genre_to_unsubscripe + (tracker_names_delimiter+' ').join(subscribed_genres))

#
#converts user's state from selecting tracker to selecting genre
#

def switch_users_state_forward(user):
    if user.state == states['choosing_tracker_to_subscribe']:
        user.state = states['choosing_genre_to_subscribe']
    elif user.state == states['choosing_tracker_to_unsubscribe']:
        user.state = states['choosing_genre_to_unsubscribe']

#
#handles user's answer after he have been asked to select trackers
#

def handle_selecting_trackers(user, obj, bot, chat_id, session):
    result = handle_users_trackers_list(obj, user.state)
    selected_trackers = result.get('selected_trackers')
    if selected_trackers is None:
        return
    genred = result.get('genred')
    switch_users_state_forward(user)
    user.trackers_to_subscribe = selected_trackers
    if not genred:
        send_plain(bot = bot, chat_id = chat_id, message = msg_subscription_set)
        start_changing_registering(user.state, chat_id, user.trackers_to_subscribe, [any_keyword])
        user.state = states['undefined']
        session.flush()
        return
    summon_user_to_select_genre(user, bot, chat_id)
    session.flush()
    return

#
#handles user's answer after he have been asked to select genres
#

def handle_selecting_genres(user, obj, bot, chat_id, session):
    result = handle_users_genres_list(obj, user.state)
    selected_genres = result.get('selected_trackers')
    if selected_genres is None:
        return
    send_plain(bot = bot, chat_id = chat_id, message = msg_subscription_set)
    start_changing_registering(user.state, chat_id, user.trackers_to_subscribe, selected_genres)
    user.state = states['undefined']
    session.flush()

#
#handles user's message after he hasn't got appropriate state for searching movies
#

@print_exceptions
def handle_subscription_request(bot, update):
    #try:
    chat_id = update['message']['chat']['id']

    user = get_user(chat_id)
    session = get_session()

    if user is not None and (user.state == states['choosing_tracker_to_subscribe'] or user.state == states['choosing_tracker_to_unsubscribe']):
        handle_selecting_trackers(user, update['message']['text'], bot, chat_id, session)
    elif user is not None and (user.state == states['choosing_genre_to_subscribe'] or user.state == states['choosing_genre_to_unsubscribe']):
        handle_selecting_genres(user, update['message']['text'], bot, chat_id, session)
    #except Exception:
    #    print(sys.exc_info()[1])
    #    print(traceback.print_tb(sys.exc_info()[2]))

#
#handles user's reply to asking him for giving title for search
#

@print_exceptions
def handle_movie_request(bot, update):
    #try:
    chat_id = update['message']['chat']['id']
    title = update['message']['text']

    user = get_user(chat_id)
    session = get_session()

    if user is not None and user.state == states['searching']:
        send_advanced_single_movie_info(bot, user, session, get_advanced_movie_info_by_title(title))
        user.state = states['undefined']
        session.flush()
    else:# if state is not correct for commiting search
        handle_subscription_request(bot, update)
    #except Exception:
    #    print(sys.exc_info()[1])
    #    print(traceback.print_tb(sys.exc_info()[2]))
