import sys
import traceback

#from shared import users

from user import get_user, create_user
from db_connection_manager import get_session

from shared import pa
from shared import ya

from constants import states

from keyboard_markups import action_reply_markup

from wiki_manager import send_wiki_section_info

from movies_manager import send_first_movie_msg, update_movies, increase_index, send_movie_info

from string_converting import split

#from user import User

from constants import states

from action_handlers import handle_action

def set_tracker(chat_id, tracker):
    user = get_user(chat_id)
    session = get_session()

    if user is None:
        user = create_user(chat_id, tracker, states['selecting_genre'])
    else:
        user.tracker = tracker
        if user.indexes.get(tracker) is None:
            user.indexes[tracker] = {}
            user.pages[tracker] = {}

    session.flush()

def set_genre(chat_id, genre, bot):
    user = get_user(chat_id)
    session = get_session()

    if user is None:
        bot.sendMessage(chat_id = chat_id, text = msg_tracker_is_not_set)
        return
    elif user.tracker == 'pbay':
        bot.sendMessage(chat_id = chat_id, text = msg_invalid_command_for_tracker)
        return

    user.genre = genre
    user.state = states['iterating']

    if user.indexes[user.tracker].get(genre) is None:
        user.indexes[user.tracker][genre] = 0
        user.pages[user.tracker][genre] = 1
        update_movies(chat_id)
    else:
        increase_index(chat_id)

    send_movie_info(bot, chat_id)

    session.flush()

def handle_decision(bot, chat_id, answer):
    user = get_user(chat_id)
    session = get_session()

    if answer == 'yes':
        bot.sendMessage(chat_id = chat_id, text = "Ok, let's try to do it again")
    else:
        bot.sendMessage(chat_id = chat_id, text = "As you wish")
        user.state = states['undefined']

    session.flush()

def handle_callback(bot, update):
    try:
        callback_data = split(update.callback_query.data, maxsplit = 1)
        callback_type = callback_data[0]
        callback_value = callback_data[1]

        chat_id = update.callback_query.message.chat.id

        if callback_type == 'genre':
            set_genre(chat_id, callback_value, bot)

        elif callback_type == 'tracker':
            set_tracker(chat_id, callback_value)
            bot.sendMessage(chat_id = chat_id, text = 'Ok, tracker has been switched')

            if callback_value == 'pbay' or callback_value == 'mine' or callback_value == 'act':
                send_first_movie_msg(bot, chat_id, callback_value)

        elif callback_type == 'action':
            handle_action(chat_id, callback_value, bot)

        elif callback_type == 'wikisection':
            send_wiki_section_info(bot, chat_id, callback_value)

        elif callback_type == 'decision':
            handle_decision(bot, chat_id, callback_value)

    except Exception:
        print(sys.exc_info()[1])
        print(traceback.print_tb(sys.exc_info()[2]))
