from main import users
from main import pa
from main import ya

from constants import states

from keyboard_markups import action_reply_markup

from wiki_manager import send_wiki_section_info

from movies_manager import send_first_movie_msg

def set_tracker(chat_id, tracker):

    if users.get(chat_id) is None:
        users[chat_id] = User(states['selecting_genre'], tracker)
    else:
        users[chat_id].tracker = tracker
        if users[chat_id].indexes.get(tracker) is None:
            users[chat_id].indexes[tracker] = {}
            users[chat_id].pages[tracker] = {}

def set_genre(chat_id, genre, bot):

    if users.get(chat_id) is None:
        bot.sendMessage(chat_id = chat_id, text = msg_tracker_is_not_set)
        return
    elif users.get(chat_id).tracker == 'pbay':
        bot.sendMessage(chat_id = chat_id, text = msg_invalid_command_for_tracker)
        return

    users[chat_id].genre = genre
    users[chat_id].state = states['iterating']

    if users[chat_id].indexes[users[chat_id].tracker].get(genre) is None:
        users[chat_id].indexes[users[chat_id].tracker][genre] = 0
        users[chat_id].pages[users[chat_id].tracker][genre] = 1
        update_movies(chat_id)
    else:
        increase_index(chat_id)

    send_movie_info(bot, chat_id)

def handle_callback(bot, update):
    callback_data = split(update.callback_query.data, maxsplit = 1)
    callback_type = callback_data[0]
    callback_value = callback_data[1]

    chat_id = update.callback_query.message.chat.id

    if callback_type == 'genre':
        set_genre(chat_id, callback_value, bot)

    elif callback_type == 'tracker':
        set_tracker(chat_id, callback_value)
        bot.sendMessage(chat_id = chat_id, text = 'Ok, tracker has been switched')

        if callback_value == 'pbay' or callback_value == 'mine':
            send_first_movie_msg(bot, chat_id, callback_value)

    elif callback_type == 'action':
        handle_action(chat_id, callback_value, bot)

    elif callback_type == 'wikisection':
        send_wiki_section_info(bot, chat_id, callback_value)