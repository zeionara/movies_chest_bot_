from shared import users

from keyboard_markups import action_reply_markup

from constants import msg_tracker_is_not_set
from constants import msg_genre_is_not_set

from reviews_manager import get_movie_id
from reviews_manager import get_movie_review_list_index
from reviews_manager import update_reviews, send_review_info

from movies_manager import increase_index, send_movie_info

from reviews_manager import increase_reviews_index

from wiki_manager import send_wiki_info

def handle_next_action(chat_id, provider, index, searching_movies):
    if searching_movies:
        increase_index(chat_id)
    else:
        if provider == 'rt':
            increase_reviews_index(chat_id)
        elif provider == 'imdb' or provider == 'kp':
            users[chat_id].review_indexes[index] += 1

def hanle_flush_action(chat_id, provider, index, searching_movies):
    user = users[chat_id]

    if searching_movies and user.pages[tracker][genre] == 1:
        users[chat_id].indexes[tracker][genre] = 0
    elif searching_movies:
        users[chat_id].pages[tracker][genre] = 1
        update_movies(chat_id)
    else:
        if provider == 'rt':
            users[chat_id].review_indexes[index][users[chat_id].reviews_group] = 0
        elif provider == 'kp' or provider == 'imdb':
            users[chat_id].review_indexes[index] = 0

def handle_imdbrev_action(chat_id):
    if users[chat_id].imdb_id is not None:
        provider = 'imdb'
        users[chat_id].reviews_provider = provider

        id = users[chat_id].imdb_id
        index = get_movie_review_list_index(provider, id)
        users[chat_id].searching_movies = False

        update_reviews(chat_id)

        if users[chat_id].review_indexes.get(index) is None:
            users[chat_id].review_indexes[index] = 0
        else:
            users[chat_id].review_indexes[index] += 1

def handle_kprev_action(chat_id):
    provider = 'kp'
    users[chat_id].reviews_provider = provider

    id = users[chat_id].current_title
    index = get_movie_review_list_index(provider, id)
    users[chat_id].searching_movies = False

    update_reviews(chat_id)

    if users[chat_id].review_indexes.get(index) is None:
        users[chat_id].review_indexes[index] = 0
    else:
        print(users[chat_id].review_indexes)
        print(index)
        users[chat_id].review_indexes[index] += 1

def handle_rtrev_action(chat_id, action):
    if action == 'rtcrev':
        users[chat_id].reviews_group = 'critics'
    else:
        users[chat_id].reviews_group = 'audience'

    provider = 'rt'
    users[chat_id].reviews_provider = provider

    id = users[chat_id].current_title
    index = get_movie_review_list_index(provider, id)
    users[chat_id].searching_movies = False

    if users[chat_id].review_pages.get(index) is None:
        page = users[chat_id].review_pages[index] = {}
    if users[chat_id].review_pages[index].get(users[chat_id].reviews_group) is None:
        users[chat_id].review_pages[index][users[chat_id].reviews_group] = 1

    update_reviews(chat_id)

    if users[chat_id].review_indexes.get(index) is None:
        users[chat_id].review_indexes[index] = {}
    if users[chat_id].review_indexes[index].get(users[chat_id].reviews_group) is None:
        users[chat_id].review_indexes[index][users[chat_id].reviews_group] = 0
    else:
        increase_reviews_index(chat_id)

def handle_action(chat_id, action, bot):

    searching_movies = users[chat_id].searching_movies

    changing_iterating_state = action == 'imdbrev' or action == 'kprev' or action == 'rtcrev' or action == 'rtarev' or action == 'wiki'

    if users.get(chat_id) is None and searching_movies and not changing_iterating_state:
        bot.sendMessage(chat_id = chat_id, text = msg_tracker_is_not_set)
        return
    elif users[chat_id].genre is None and searching_movies and not changing_iterating_state:
        bot.sendMessage(chat_id = chat_id, text = msg_genre_is_not_set)
        return

    if searching_movies and not changing_iterating_state:
        tracker = users[chat_id].tracker
        genre = users[chat_id].genre

    provider = users[chat_id].reviews_provider

    id = get_movie_id(chat_id)
    index = get_movie_review_list_index(provider, id)

    if action == 'flush':
        handle_flush_action(chat_id, provider, index, searching_movies)
    elif action == 'next':
        handle_next_action(chat_id, provider, index, searching_movies)
    elif action == 'imdbrev':
        handle_imdbrev_action(chat_id)
    elif action == 'kprev':
        handle_kprev_action(chat_id)
    elif (action == 'rtcrev' or action == 'rtarev'):
        handle_rtrev_action(chat_id, action)
    elif action == 'imdbrevexit':
        users[chat_id].searching_movies = True
        increase_index(chat_id)
    elif action == 'wiki':
        send_wiki_info(bot, chat_id, users[chat_id].current_title)
        return

    if users[chat_id].searching_movies:
        send_movie_info(bot, chat_id)
    else:
        send_review_info(bot, chat_id)
