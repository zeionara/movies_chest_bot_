from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

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
#main keyboard
#
tracker_btn = KeyboardButton("/tracker")
genre_btn = KeyboardButton("/genre")
search_btn = KeyboardButton("/search")
subscribe_btn = KeyboardButton("/subscribe")
unsubscribe_btn = KeyboardButton("/unsubscribe")
keyboard_btn = KeyboardButton("/keyboard")

main_reply_markup = ReplyKeyboardMarkup([[tracker_btn, genre_btn, search_btn], [subscribe_btn, unsubscribe_btn, keyboard_btn]],
                                        resize_keyboard = True, selective = True)
main_reply_markup_remove = ReplyKeyboardRemove(remove_keyboard = True, selective = True)

#
#yes/no
#
yes_btn = InlineKeyboardButton("yes", callback_data = join('decision', 'yes'))
no_btn = InlineKeyboardButton("no", callback_data = join('decision', 'no'))
yes_no_reply_markup = InlineKeyboardMarkup([[yes_btn, no_btn]])

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

def get_wiki_buttons_array(sections):
    btns = []
    current_keyboard_string = []
    current_buttons_per_string = 0

    for section in sections:
        current_buttons_per_string += 1
        if current_buttons_per_string > buttons_per_string_in_wiki_markup:
            btns.append(current_keyboard_string)
            current_keyboard_string = []
            current_buttons_per_string = 1
        current_keyboard_string.append(section)

    return btns

def wiki_buttons_array_to_keyboard_markup(buttons_array):
    btns = []
    current_keyboard_string = []
    current_buttons_per_string = 0

    keyboard_array = []
    for buttons_line in buttons_array:
        keyboard_line = []
        for section in buttons_line:
            keyboard_line.append(InlineKeyboardButton(section.lower(), callback_data = join('wikisection', section)))
        keyboard_array.append(keyboard_line)
    keyboard_array.append([back_btn])

    return InlineKeyboardMarkup(keyboard_array)

def get_wiki_keyboard_markup(sections):
    return InlineKeyboardMarkup(get_wiki_buttons(sections))

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
