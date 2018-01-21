#
#python
#

import telegram
import time

#
#resources
#

from constants import delay_between_message_sequence

#
#tools
#

from string_converting import chunkstring

#
#send simple short text message
#

def send_plain(bot, chat_id, message, reply_markup = None, reply_to_message_id = None):

    message = message.encode().decode('utf-8', 'ignore')

    if message is None or message == '':
        message = 'n/a'

    if reply_to_message_id is None:
        if reply_markup is None:
            bot.sendMessage(chat_id, message)
        else:
            bot.sendMessage(chat_id, message, reply_markup = reply_markup)
    else:
        if reply_markup is None:
            bot.sendMessage(chat_id, message, reply_to_message_id = reply_to_message_id)
        else:
            bot.sendMessage(chat_id, message, reply_markup = reply_markup, reply_to_message_id = reply_to_message_id)

#
#send long text message possibly with an image and reply markup
#

def send_chunked(bot, chat_id, message, image = None, reply_markup = None):

    message = message.encode().decode('utf-8', 'ignore')

    if image is not None:
        try:
            bot.sendPhoto(chat_id, image)
        except telegram.error.NetworkError:
            print('Wrong picture ' + str(image))
        else:
            time.sleep(delay_between_message_sequence)

    if message is None or message == '':
        message = 'n/a'

    chunks = chunkstring(message)

    for chunk in chunks[:-1]:
        try:
            bot.sendMessage(chat_id, chunk)
        except UnicodeEncodeError:
            print('Wrong chunk')
        else:
            time.sleep(delay_between_message_sequence)

    try:
        if reply_markup is None:
            bot.sendMessage(chat_id, chunks[-1])
        else:
            bot.sendMessage(chat_id, chunks[-1], reply_markup = reply_markup)
    except UnicodeEncodeError:
        print('Wrong final chunk')
    except telegram.error.BadRequest:
        bot.sendMessage(chat_id, "n/a", reply_markup = reply_markup)

#
#send long text message with alternative variants of reply markups and possibly with an image
#

def send_chunked_forked(bot, chat_id, message, reply_markups, conditions, image = None):
    for i in range(len(conditions)):
        if conditions[i]:
            send_chunked(bot, chat_id, message, image = image, reply_markup = reply_markups[i])
            return
    send_chunked(bot, chat_id, message, image = image, reply_markup = reply_markups[-1])
