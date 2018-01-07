import sys
import datetime
import os

import pickle
import redis
import configparser
import requests

from collections import namedtuple
from threading import Thread

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, filters

sys.path.append("adapters/")
sys.path.append("tools/")

from string_converting import join
from string_converting import split
from string_converting import chunkstring

from yuptorrents import YuptorrentsAdapter
from piratebay import PiratebayAdapter
import youtube
import imdb
import kinopoisk_
import rotten_tomatoes
import wikipedia_
import kudago
from top_movies import get_top_movies

import expire_controller

from constants import delimiter
from constants import redis_key_delimiter
from constants import time_prefix
from constants import creation_time_prefix
from constants import reviews_prefix
from constants import buttons_per_string_in_wiki_markup
from constants import max_message_length
from constants import states
from constants import genres
from constants import forbidden_movie_fields
from constants import telegram_token

from redis_connector import redis_connection
from redis_connector import write_to_redis
from redis_connector import update_redis_time

from keyboard_markups import tracker_reply_markup
from keyboard_markups import genre_reply_markup
from keyboard_markups import action_reply_markup
from keyboard_markups import action_reply_markup_extended
from keyboard_markups import action_reply_markup_reduced

from keyboard_markups import action_reply_markup_review_imdb

from keyboard_markups import action_reply_markup_review_kp
from keyboard_markups import action_reply_markup_review_kp_extended

from keyboard_markups import action_reply_markup_review_rtc
from keyboard_markups import action_reply_markup_review_rtc_extended

from keyboard_markups import action_reply_markup_review_rta
from keyboard_markups import action_reply_markup_review_rta_extended

from user import User

Movie = namedtuple('Movie','title poster description trailer')
MovieHeader = namedtuple('MovieHeader','title href')
MovieExtendedHeader = namedtuple('MovieExtendedHeader','title href id')



thread = Thread(target = expire_controller.inspect_enhanced, args = (10, ))
thread.start()

#globals
ya = YuptorrentsAdapter()
pa = PiratebayAdapter()

users = {}

def main():

    updater = Updater(telegram_token)

    updater.dispatcher.addHandler(CommandHandler('genre', command_handlers.genre))
    updater.dispatcher.addHandler(CommandHandler('tracker', command_handlers.tracker))
    updater.dispatcher.addHandler(CommandHandler('search', command_handlers.search))
    updater.dispatcher.addHandler(CallbackQueryHandler(handle_callback))
    updater.dispatcher.addErrorHandler(print_error)
    updater.dispatcher.addHandler(MessageHandler(filters.TEXT, handle_movie_request))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
