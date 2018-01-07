from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from constants import genres
from constants import buttons_per_string_in_genres_markup
from constants import buttons_per_string_in_wiki_markup

from string_converting import join

def get_genres_buttons():

    counter = 0
    result = []
    local_result = []

    for genre in genres:
        genre_lower = genre.lower()

        if counter == buttons_per_string_in_genres_markup:
            result.append(local_result)
            local_result = []
            counter = 0

        if counter < buttons_per_string_in_genres_markup:
            local_result.append(InlineKeyboardButton(genre_lower, callback_data = join('genre', genre)))
            counter += 1

    return result

#
#tracker selection menu
#
yup_btn = InlineKeyboardButton("New torrents from yuptorrents", callback_data = join('tracker', 'yup'))
pbay_btn = InlineKeyboardButton("New torrents from piratebay", callback_data = join('tracker', 'pbay'))
new_btn = InlineKeyboardButton("The gold collection", callback_data = join('tracker', 'mine'))
act_btn = InlineKeyboardButton("Actual movies (now in the cinemas)", callback_data = join('tracker', 'act'))

tracker_reply_markup = InlineKeyboardMarkup([[yup_btn], [pbay_btn], [new_btn], [act_btn]])

#
#genre selection menu
#
genre_reply_markup = InlineKeyboardMarkup(get_genres_buttons())

#
#action selection menu
#
kinopoisk_btn = InlineKeyboardButton("kinopoisk reviews", callback_data = join('action', 'kprev'))
imdb_btn = InlineKeyboardButton("imdb reviews", callback_data = join('action', 'imdbrev'))
rtc_btn = InlineKeyboardButton("rottentomatoes critics reviews", callback_data = join('action', 'rtcrev'))
rta_btn = InlineKeyboardButton("rottentomatoes audience reviews", callback_data = join('action', 'rtarev'))
next_btn = InlineKeyboardButton("next", callback_data = join('action', 'next'))
flush_btn = InlineKeyboardButton("flush", callback_data = join('action', 'flush'))
back_btn = InlineKeyboardButton("back to search for movies", callback_data = join('action', 'imdbrevexit'))
wiki_btn = InlineKeyboardButton("search in wikipedia", callback_data = join('action', 'wiki'))

action_reply_markup = InlineKeyboardMarkup([[next_btn, flush_btn], [kinopoisk_btn], [rtc_btn, rta_btn], [wiki_btn]])
action_reply_markup_extended = InlineKeyboardMarkup([[next_btn, flush_btn], [imdb_btn, kinopoisk_btn], [rtc_btn, rta_btn], [wiki_btn]])
action_reply_markup_reduced = InlineKeyboardMarkup([[imdb_btn, kinopoisk_btn], [rtc_btn, rta_btn], [wiki_btn]])
action_reply_markup_extremely_reduced = InlineKeyboardMarkup([[kinopoisk_btn], [rtc_btn, rta_btn], [wiki_btn]])

action_reply_markup_review_imdb = InlineKeyboardMarkup([[next_btn, flush_btn], [back_btn, kinopoisk_btn], [rtc_btn, rta_btn], [wiki_btn]])

action_reply_markup_review_kp = InlineKeyboardMarkup([[next_btn, flush_btn], [back_btn], [rtc_btn, rta_btn], [wiki_btn]])
action_reply_markup_review_kp_extended = InlineKeyboardMarkup([[next_btn, flush_btn], [back_btn, imdb_btn], [rtc_btn, rta_btn], [wiki_btn]])

action_reply_markup_review_rtc = InlineKeyboardMarkup([[next_btn, flush_btn], [back_btn, kinopoisk_btn], [rta_btn], [wiki_btn]])
action_reply_markup_review_rtc_extended = InlineKeyboardMarkup([[next_btn, flush_btn], [back_btn, imdb_btn], [kinopoisk_btn, rta_btn], [wiki_btn]])

action_reply_markup_review_rta = InlineKeyboardMarkup([[next_btn, flush_btn], [back_btn, kinopoisk_btn], [rtc_btn], [wiki_btn]])
action_reply_markup_review_rta_extended = InlineKeyboardMarkup([[next_btn, flush_btn], [back_btn, imdb_btn], [kinopoisk_btn, rtc_btn], [wiki_btn]])

def get_wiki_buttons(sections):
    btns = []
    current_keyboard_string = []
    current_buttons_per_string = 0

    for section in sections:
        current_buttons_per_string += 1
        if current_buttons_per_string > buttons_per_string_in_wiki_markup:
            btns.append(current_keyboard_string)
            current_keyboard_string = []
            current_buttons_per_string = 1
        current_keyboard_string.append(InlineKeyboardButton(section.lower(), callback_data = join('wikisection', section)))
    btns.append([back_btn])

    return btns

def get_wiki_keyboard_markup(sections):
    return InlineKeyboardMarkup(get_wiki_buttons(sections))
