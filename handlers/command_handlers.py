#
#python
#

import sys
import traceback

#
#odm
#

from user import get_user, create_user

#
#resources
#

import shared
from keyboard_markups import genre_reply_markup, tracker_reply_markup, main_reply_markup, main_reply_markup_remove
from constants import msg_tracker_is_not_set, msg_invalid_command_for_tracker, msg_choose_genre, msg_choose_tracker,\
    msg_send_me_title_for_search, msg_coming_soon, msg_keyboard_set, msg_keyboard_removed,\
    msg_choose_tracker_to_subscripe, msg_no_subscriptions, msg_choose_tracker_to_unsubscripe,\
    states, tracker_names, tracker_names_delimiter, genred_trackers,\
    rotten_tomatoes_reviews_provider, imdb_reviews_provider, kinopoisk_reviews_provider

#
#managers
#

from db_connection_manager import get_session
from message_manager import send_plain
from subscriptions_manager import get_subscribed_tracker_names

#
#decorators
#

from exception_handling_decorators import print_exceptions

#
#handles user's request for selecting genre
#

@print_exceptions
def select_genre(bot, update):
    #try:
    chat_id = update.message.chat_id

    user = get_user(chat_id)

    if user is None:
        send_plain(bot = bot, chat_id = chat_id, message = msg_tracker_is_not_set)
        return
    elif user.tracker not in genred_trackers:
        send_plain(bot = bot, chat_id = chat_id, message = msg_invalid_command_for_tracker)
        return

    send_plain(bot = bot, chat_id = chat_id, message = msg_choose_genre, reply_markup = genre_reply_markup)
    #except Exception:
    #    print(sys.exc_info()[1])
    #    print(traceback.print_tb(sys.exc_info()[2]))

#
#handles user's request for selecting tracker
#

@print_exceptions
def select_tracker(bot, update):
    #try:
    chat_id = update.message.chat_id

    user = get_user(chat_id)
    session = get_session()

    if user is not None and not user.searching_movies:
        user.searching_movies = True
        session.flush()

    send_plain(bot = bot, chat_id = chat_id, message = msg_choose_tracker, reply_markup = tracker_reply_markup)
    #except Exception:
    #    print(sys.exc_info()[1])
    #    print(traceback.print_tb(sys.exc_info()[2]))

#
#handles user's request for switching keyboard
#

@print_exceptions
def switch_keyboard(bot, update):
    #try:
    user = get_user(update.message.chat_id)

    if not user.main_keyboard_active:
        send_plain(bot = bot, chat_id = update.message.chat_id, message = msg_keyboard_set,
            reply_markup = main_reply_markup, reply_to_message_id = update.message.message_id)
        user.main_keyboard_active = True
    else:
        send_plain(bot = bot, chat_id = update.message.chat_id, message = msg_keyboard_removed,
            reply_markup = main_reply_markup_remove, reply_to_message_id = update.message.message_id)
        user.main_keyboard_active = False
    #except Exception:
    #    print(sys.exc_info()[1])
    #    print(traceback.print_tb(sys.exc_info()[2]))

#
#handles user's request for subscribing
#

@print_exceptions
def subscribe(bot, update):
    #try:
    chat_id = update.message.chat_id

    user = get_user(chat_id)
    session = get_session()

    if user is None:
        user = create_user(chat_id, yuptorrents_tracker, states['choosing_tracker_to_subscribe'])
    else:
        user.state = states['choosing_tracker_to_subscribe']
        session.flush()

    send_plain(bot = bot, chat_id = chat_id, message = msg_choose_tracker_to_subscripe + (tracker_names_delimiter+' ').join(tracker_names))
    #except Exception:
    #    print(sys.exc_info()[1])
    #    print(traceback.print_tb(sys.exc_info()[2]))

#
#handles user's request for unsubscribing
#

@print_exceptions
def unsubscribe(bot, update):
    #try:
    chat_id = update.message.chat_id

    user = get_user(chat_id)
    session = get_session()

    subscribed_tracker_names = get_subscribed_tracker_names(chat_id)

    if user is None or len(subscribed_tracker_names) == 0:
        send_plain(bot = bot, chat_id = chat_id, message = msg_no_subscriptions)
        return

    user.state = states['choosing_tracker_to_unsubscribe']
    user.tmp = subscribed_tracker_names
    session.flush()

    send_plain(bot = bot, chat_id = chat_id, message = msg_choose_tracker_to_unsubscripe + (tracker_names_delimiter+' ').join(subscribed_tracker_names))
    #except Exception:
    #    print(sys.exc_info()[1])
    #    print(traceback.print_tb(sys.exc_info()[2]))

#
#handles user's request for searching for movie by it's title
#

@print_exceptions
def start_search(bot, update):
    #try:
    chat_id = update.message.chat_id

    user = get_user(chat_id)
    session = get_session()

    if user is None:
        user = create_user(chat_id, yuptorrents_tracker, states['searching'])
    else:
        user.state = states['searching']
        session.flush()

    send_plain(bot = bot, chat_id = chat_id, message = msg_send_me_title_for_search)
    #except Exception:
    #    print(sys.exc_info()[1])
    #    print(traceback.print_tb(sys.exc_info()[2]))
