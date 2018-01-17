#from shared import users
from user import get_user, create_user
from db_connection_manager import get_session

from keyboard_markups import back_btn
from keyboard_markups import get_wiki_keyboard_markup

from string_converting import chunkstring

import wikipedia_adapter

def send_wiki_info(bot, chat_id, title):
    user = get_user(chat_id)
    session = get_session()

    info = wikipedia_adapter.get_movie_details(title)

    user.wiki_content = info['content']
    sections = info['sections']
    synopsis = info['synopsis']

    keyboard_markup = get_wiki_keyboard_markup(sections)

    user.wiki_keyboard_markup = keyboard_markup

    response = bot.sendMessage(chat_id = chat_id, text = synopsis, reply_markup = keyboard_markup)
    session.flush()
    return response

def send_wiki_section_info(bot, chat_id, section):
    user = get_user(chat_id)
    session = get_session()

    chunks = chunkstring(user.wiki_content.get(section))
    for chunk in chunks[:-1]:
        bot.sendMessage(chat_id, chunk)

    if chunks[-1] == '':
        chunks[-1] = 'n/a'
    response = bot.sendMessage(chat_id = chat_id, text = chunks[-1], reply_markup = user.wiki_keyboard_markup)
    session.flush()
    return response
