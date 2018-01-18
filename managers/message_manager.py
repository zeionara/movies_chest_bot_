import telegram
import time
from string_converting import chunkstring
from constants import delay_between_message_sequence

#
#send simple short text message
#

def send_plain(bot, chat_id, message, reply_markup = None):
    if reply_markup is None:
        bot.sendMessage(chat_id, message)
    else:
        bot.sendMessage(chat_id, message, reply_markup = reply_markup)

#
#send long text message possibly with an image and reply markup
#

def send_chunked(bot, chat_id, message, image = None, reply_markup = None):
    if image is not None:
        try:
            bot.sendPhoto(chat_id, image)
            time.sleep(delay_between_message_sequence)
        except telegram.error.NetworkError:
            print('Wrong picture ' + str(image))

    chunks = chunkstring(message)

    for chunk in chunks[:-1]:
        bot.sendMessage(chat_id, chunk)
        time.sleep(delay_between_message_sequence)

    if reply_markup is None:
        bot.sendMessage(chat_id, chunks[-1])
    else:
        bot.sendMessage(chat_id, chunks[-1], reply_markup = reply_markup)

#
#send long text message with alternative variants of reply markups and possibly with an image
#

def send_chunked_forked(bot, chat_id, message, reply_markups, conditions, image = None):
    for i in range(len(conditions)):
        if conditions[i]:
            send_chunked(bot, chat_id, message, image = image, reply_markup = reply_markups[i])
            return
    send_chunked(bot, chat_id, message, image = image, reply_markup = reply_markups[-1])
