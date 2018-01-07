from main import users

from movies_manager import send_advanced_single_movie_info
from movies_manager import get_advanced_movie_info_by_title

from constants import states

def handle_movie_request(bot, update):

    chat_id = update['message']['chat']['id']
    title = update['message']['text']

    if users.get(chat_id) is not None and users[chat_id].state == states['searching']:
         send_advanced_single_movie_info(bot, chat_id, get_advanced_movie_info_by_title(title))

    users[chat_id].state = states['undefined']
