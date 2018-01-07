import sys
import traceback

from keyboard_markups import genre_reply_markup
from keyboard_markups import tracker_reply_markup

from constants import msg_tracker_is_not_set
from constants import msg_invalid_command_for_tracker
from constants import msg_choose_genre
from constants import msg_choose_tracker
from constants import msg_send_me_title_for_search
from constants import msg_coming_soon
from constants import tracker_names
from constants import msg_choose_tracker_to_subscripe, tracker_names_delimiter

from shared import users
from user import User

from constants import states

def select_genre(bot, update):

    chat_id = update.message.chat_id

    if users.get(chat_id) is None:
        bot.sendMessage(chat_id = chat_id, text = msg_tracker_is_not_set)
        return

    elif users.get(chat_id).tracker == 'pbay' or users.get(chat_id).tracker == 'mine':
        bot.sendMessage(chat_id = chat_id, text = msg_invalid_command_for_tracker)
        return

    response = bot.sendMessage(chat_id = update.message.chat_id, text = msg_choose_genre, reply_markup = genre_reply_markup)
    return response

def select_tracker(bot, update):
    response = bot.sendMessage(chat_id = update.message.chat_id, text = msg_choose_tracker, reply_markup = tracker_reply_markup)
    return response

def subscribe(bot, update):
    print('got')
    try:
        chat_id = update.message.chat_id

        if users.get(chat_id) is None:
            users[chat_id] = User(states['choosing_tracker_to_subscribe'], 'yup')
        else:
            users[chat_id].state = states['choosing_tracker_to_subscribe']

        response = bot.sendMessage(chat_id = chat_id, text = msg_choose_tracker_to_subscripe + tracker_names_delimiter.join(tracker_names))

        return response
    except Exception:
        print(sys.exc_info()[1])
        print(traceback.print_tb(sys.exc_info()[2]))

def start_search(bot, update):
    try:
        chat_id = update.message.chat_id

        if users.get(chat_id) is None:
            users[chat_id] = User(states['searching'], 'yup')
        else:
            users[chat_id].state = states['searching']

        response = bot.sendMessage(chat_id = chat_id, text = msg_send_me_title_for_search)

        return response
    except Exception:
        print(sys.exc_info()[1])
        print(traceback.print_tb(sys.exc_info()[2]))
