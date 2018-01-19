import sys
import traceback

from keyboard_markups import genre_reply_markup
from keyboard_markups import tracker_reply_markup
from keyboard_markups import main_reply_markup, main_reply_markup_remove

from constants import msg_tracker_is_not_set
from constants import msg_invalid_command_for_tracker
from constants import msg_choose_genre
from constants import msg_choose_tracker
from constants import msg_send_me_title_for_search
from constants import msg_coming_soon
from constants import tracker_names
from constants import msg_choose_tracker_to_subscripe, tracker_names_delimiter, msg_no_subscriptions, msg_choose_tracker_to_unsubscripe
from shared import main_keyboard_active

from shared import users
#from user import User
from user import get_user, create_user
from db_connection_manager import get_session


from constants import states

from subscriptions_manager import get_subscribed_tracker_names

def select_genre(bot, update):
    chat_id = update.message.chat_id
    print('selecting genre')
    user = get_user(chat_id)
    session = get_session()
    print('selecting genre')
    try:

        print('selecting genre')
        if user is None:
            print('selecting genrei')
            bot.sendMessage(chat_id = chat_id, text = msg_tracker_is_not_set)
            return
        elif user.tracker == 'pbay' or user.tracker == 'mine':
            print('selecting genree')
            bot.sendMessage(chat_id = chat_id, text = msg_invalid_command_for_tracker)
            return

        response = bot.sendMessage(chat_id = update.message.chat_id, text = msg_choose_genre, reply_markup = genre_reply_markup)

        session.flush()
        return response
    except Exception:
        print(sys.exc_info()[1])
        print(traceback.print_tb(sys.exc_info()[2]))

def select_tracker(bot, update):
    user = get_user(update.message.chat_id)
    session = get_session()

    if user is not None and not user.searching_movies:
        user.searching_movies = True

    response = bot.sendMessage(chat_id = update.message.chat_id, text = msg_choose_tracker, reply_markup = tracker_reply_markup)

    session.flush()
    return response

def switch_keyboard(bot, update):
    if not main_keyboard_active:
        response = bot.sendMessage(chat_id = update.message.chat_id, reply_to_message_id = update.message.message_id,
                                    text = 'Ok, keyboard is here', reply_markup = main_reply_markup)
        main_keyboard_active = True
    else:
        response = bot.sendMessage(chat_id = update.message.chat_id, reply_to_message_id = update.message.message_id,
                                    text = 'Ok, keyboard is removed', reply_markup = main_reply_markup_remove)
        main_keyboard_active = False
    return response

def subscribe(bot, update):
    chat_id = update.message.chat_id
    user = get_user(chat_id)
    session = get_session()

    print('got')
    try:


        if user is None:
            user = create_user(chat_id, 'yup', states['choosing_tracker_to_subscribe'])#User(states['choosing_tracker_to_subscribe'], 'yup')
        else:
            user.state = states['choosing_tracker_to_subscribe']

        response = bot.sendMessage(chat_id = chat_id, text = msg_choose_tracker_to_subscripe + (tracker_names_delimiter+' ').join(tracker_names))


        session.flush()
        return response
    except Exception:
        print(sys.exc_info()[1])
        print(traceback.print_tb(sys.exc_info()[2]))

def unsubscribe(bot, update):
    chat_id = update.message.chat_id
    user = get_user(chat_id)
    session = get_session()

    print('got')
    try:


        subscribed_tracker_names = get_subscribed_tracker_names(chat_id)

        if user is None or len(subscribed_tracker_names) == 0:
            bot.sendMessage(chat_id = chat_id, text = msg_no_subscriptions)
            return

        user.state = states['choosing_tracker_to_unsubscribe']
        user.tmp = subscribed_tracker_names

        print(subscribed_tracker_names)
        bot.sendMessage(chat_id = chat_id, text = msg_choose_tracker_to_unsubscripe + (tracker_names_delimiter+' ').join(subscribed_tracker_names))
        session.flush()
        return
    except Exception:
        print(sys.exc_info()[1])
        print(traceback.print_tb(sys.exc_info()[2]))

def start_search(bot, update):
    chat_id = update.message.chat_id
    user = get_user(chat_id)
    session = get_session()

    try:


        if user is None:
            user = create_user(chat_id, 'yup', states['searching'])
        else:
            user.state = states['searching']

        response = bot.sendMessage(chat_id = chat_id, text = msg_send_me_title_for_search)
        session.flush()
        return response
    except Exception:
        print(sys.exc_info()[1])
        print(traceback.print_tb(sys.exc_info()[2]))
