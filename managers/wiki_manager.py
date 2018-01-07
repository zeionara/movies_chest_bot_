from shared import users
from keyboard_markups import back_btn
from keyboard_markups import get_wiki_keyboard_markup

from string_converting import chunkstring

import wikipedia_adapter

def send_wiki_info(bot, chat_id, title):

    info = wikipedia_adapter.get_movie_details(title)

    users[chat_id].wiki_content = info['content']
    sections = info['sections']
    synopsis = info['synopsis']

    keyboard_markup = get_wiki_keyboard_markup(sections)

    users[chat_id].wiki_keyboard_markup = keyboard_markup

    response = bot.sendMessage(chat_id = chat_id, text = synopsis, reply_markup = keyboard_markup)
    return response

def send_wiki_section_info(bot, chat_id, section):

    chunks = chunkstring(users[chat_id].wiki_content.get(section))
    for chunk in chunks[:-1]:
        bot.sendMessage(chat_id, chunk)

    if chunks[-1] == '':
        chunks[-1] = 'n/a'
    response = bot.sendMessage(chat_id = chat_id, text = chunks[-1], reply_markup = users[chat_id].wiki_keyboard_markup)
    return response
