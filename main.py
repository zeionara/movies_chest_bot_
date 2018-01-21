
#
#standard libs
#

import sys
from threading import Thread
import logging

#
#additional libs
#

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, filters

#
#project libs
#

sys.path.append('resources/')
sys.path.append("caching/")
sys.path.append("adapters/")
sys.path.append("handlers/")
sys.path.append("managers/")
sys.path.append("tools/")
sys.path.append("odm/")
sys.path.append("decorators/")

#caching
import expire_controller
#constants
from constants import telegram_token, logging_pattern, logging_filename
#handlers
from command_handlers import select_genre, select_tracker, start_search, subscribe, unsubscribe, switch_keyboard
from callback_handlers import handle_callback
from error_handlers import print_error
from message_handlers import handle_movie_request, handle_subscription_request

logging.basicConfig(format = logging_pattern, level = logging.DEBUG, filename = logging_filename)

def main():
    updater = Updater(telegram_token)

    thread = Thread(target = expire_controller.inspect_enhanced, args = (updater.bot, ))
    thread.start()

    updater.dispatcher.add_handler(CommandHandler('genre', select_genre))
    updater.dispatcher.add_handler(CommandHandler('tracker', select_tracker))
    updater.dispatcher.add_handler(CommandHandler('search', start_search))
    updater.dispatcher.add_handler(CommandHandler('subscribe', subscribe))
    updater.dispatcher.add_handler(CommandHandler('unsubscribe', unsubscribe))
    updater.dispatcher.add_handler(CommandHandler('keyboard', switch_keyboard))
    updater.dispatcher.add_handler(CallbackQueryHandler(handle_callback))
    updater.dispatcher.add_error_handler(print_error)
    updater.dispatcher.add_handler(MessageHandler(filters.Filters.text, handle_movie_request))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
