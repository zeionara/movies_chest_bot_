#
#odm
#

from user import get_user, create_user

#
#resources
#

from keyboard_markups import back_btn, get_wiki_keyboard_markup, get_wiki_buttons_array, wiki_buttons_array_to_keyboard_markup

#
#managers
#

from db_connection_manager import get_session
from message_manager import send_plain, send_chunked

#
#tools
#

from string_converting import chunkstring

#
#adapters
#

import wikipedia_adapter

#
#get article from wiki and send it's synopsis with a list of section's buttons
#

def send_wiki_info(user, session, callback_value, bot):
    info = wikipedia_adapter.get_movie_details(user.current_title)

    user.wiki_content = info['content']
    sections = info['sections']
    synopsis = info['synopsis']

    keyboard_markup = get_wiki_buttons_array(sections) #get_wiki_keyboard_markup(sections)

    user.wiki_keyboard_markup = keyboard_markup

    send_plain(bot = bot, chat_id = user.chat_id, message = synopsis,
                reply_markup = wiki_buttons_array_to_keyboard_markup(keyboard_markup))

    session.flush()
    return

#
#send info associated with an article's section
#

def send_wiki_section_info(user, session, section, bot):
    content = user.wiki_content.get(section)
    if content == '':
        content = 'n/a'

    send_chunked(bot = bot, chat_id = user.chat_id, message = content, image = None,
                reply_markup = wiki_buttons_array_to_keyboard_markup(user.wiki_keyboard_markup))

    return
