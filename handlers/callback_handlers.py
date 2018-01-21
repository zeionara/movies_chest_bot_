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

from shared import pa, ya
from constants import states
from constants import msg_tracker_is_not_set, msg_invalid_command_for_tracker, msg_lets_try_again, msg_declined_repeating_entering, msg_tracker_switched
from constants import user_selected_genre, user_selected_tracker, user_initialized_action, user_selected_wiki_article_section, user_answered_yes_or_no
from constants import piratebay_tracker, yuptorrents_tracker, gold_collection_tracker, actual_movies_tracker, genred_trackers
from keyboard_markups import action_reply_markup

#
#managers
#

from db_connection_manager import get_session
from wiki_manager import send_wiki_section_info
from movies_manager import send_first_movie_msg, update_movies, increase_index, send_movie_info
from message_manager import send_plain

#
#tools
#

from string_converting import split

#
#handlers
#

from action_handlers import handle_action

#
#decorators
#

from exception_handling_decorators import print_exceptions

#
#switches user to selected tracker
#

def set_tracker(user, session, tracker, bot):
    chat_id = user.chat_id

    if user is None:
        user = create_user(chat_id, tracker, states['selecting_genre'])
    else:
        user.tracker = tracker
        if user.indexes.get(tracker) is None:
            user.indexes[tracker] = {}
            user.pages[tracker] = {}

    if tracker in genred_trackers:
        send_plain(bot = bot, chat_id = chat_id, message = msg_tracker_switched)
    else:
        send_first_movie_msg(bot, user, session, tracker)

    session.flush()

#
#switches user to the selected genre
#

def set_genre(user, session, genre, bot):
    chat_id = user.chat_id

    if user is None:
        send_plain(bot = bot, chat_id = chat_id, message = msg_tracker_is_not_set)
        return
    elif user.tracker not in genred_trackers:
        send_plain(bot = bot, chat_id = chat_id, message = msg_invalid_command_for_tracker)
        return

    user.genre = genre
    user.state = states['iterating']

    if user.indexes[user.tracker].get(genre) is None:
        user.indexes[user.tracker][genre] = 0
        user.pages[user.tracker][genre] = 1
        update_movies(user, session)
    else:
        increase_index(user, session)

    send_movie_info(bot, user, session)

    session.flush()

#
#sets state to undefined if user answers 'no'
#

def handle_decision(user, session, callback_value, bot):
    chat_id = user.chat_id

    if answer == 'yes':
        send_plain(bot = bot, chat_id = chat_id, message = msg_lets_try_again)
    else:
        send_plain(bot = bot, chat_id = chat_id, message = msg_declined_repeating_entering)
        user.state = states['undefined']
        session.flush()

#
#general method for handling callbacks, given by user
#
@print_exceptions
def handle_callback(bot, update):
    #try:
    callback_data = split(update.callback_query.data, maxsplit = 1)
    callback_type = callback_data[0]
    callback_value = callback_data[1]

    user = get_user(update.callback_query.message.chat.id)
    session = get_session()

    if callback_type == user_selected_genre:
        set_genre(user, session, callback_value, bot)

    elif callback_type == user_selected_tracker:
        set_tracker(user, session, callback_value, bot)

    elif callback_type == user_initialized_action:
        handle_action(user, session, callback_value, bot)

    elif callback_type == user_selected_wiki_article_section:
        send_wiki_section_info(user, session, callback_value, bot)

    elif callback_type == user_answered_yes_or_no:
        handle_decision(user, session, callback_value, bot)

    #except Exception:
    #    print(sys.exc_info())
    #    print(sys.exc_info()[1])
    #    print(traceback.print_tb(sys.exc_info()[2]))
