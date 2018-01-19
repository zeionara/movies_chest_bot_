#from shared import users
from user import get_user, create_user
from db_connection_manager import get_session

from keyboard_markups import back_btn
from keyboard_markups import get_wiki_keyboard_markup, get_wiki_buttons_array, wiki_buttons_array_to_keyboard_markup

from string_converting import chunkstring

import wikipedia_adapter

from message_manager import send_plain, send_chunked

#
#get article from wiki and send it's synopsis with a list of section's buttons
#

def send_wiki_info(bot, chat_id, title):
    user = get_user(chat_id)
    session = get_session()

    info = wikipedia_adapter.get_movie_details(title)

    user.wiki_content = info['content']
    sections = info['sections']
    synopsis = info['synopsis']

    keyboard_markup = get_wiki_buttons_array(sections) #get_wiki_keyboard_markup(sections)

    user.wiki_keyboard_markup = keyboard_markup

    send_plain(bot = bot, chat_id = chat_id, message = synopsis,
                reply_markup = wiki_buttons_array_to_keyboard_markup(keyboard_markup))

    session.flush()
    return

#
#send info associated with an article's section
#

def send_wiki_section_info(bot, chat_id, section):
    user = get_user(chat_id)

    content = user.wiki_content.get(section)
    if content == '':
        content = 'n/a'

    send_chunked(bot = bot, chat_id = chat_id, message = content, image = None,
                reply_markup = wiki_buttons_array_to_keyboard_markup(user.wiki_keyboard_markup))

    return
