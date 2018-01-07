from bot_handler import BotHandler
from yuptorrents_adapter import YuptorrentsAdapter
import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

token = '545921711:AAE5LHkyP8DglJisg-aqQEZPvgACE_h-HBw'

bot = BotHandler(token)
ya = YuptorrentsAdapter()
greetings = ('здравствуй', 'привет', 'ку', 'здарова')
now = datetime.datetime.now()

cashed_list = None
cashed_movies = None

def send_message(chat_id, text, first_name):
    global cashed_list
    global cashed_movies

    if (cashed_list is None):
        movies = ya.get_movies_by_section('Latest')
        cashed_list = ya.movies_to_string(movies)
        cashed_movies = movies

    bot.send_message(chat_id, text.format(first_name))
    for movie in cashed_movies:
        bot.send_message(chat_id, movie.title + '\n\n\n' + movie.description + '\n\n\n' + movie.trailer)
        bot.send_photo(chat_id, movie.poster)

    #bot.send_photo(chat_id, movies[0].poster)
    #bot.send_video(chat_id, movies[0].trailer)
    #bot.send_message(chat_id, text.format(first_name) + '\n\n\n' + cashed_list)


    #movies.append(movie)

def main():
    new_offset = None
    today = now.day
    hour = now.hour
    states = {}
    movies = {}
    indexes = {}
    pages = {}
    genres = {}

    keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
                 InlineKeyboardButton("Option 2", callback_data='2')],

                [InlineKeyboardButton("Option 3", callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    while(True):

        bot.get_updates(offset = new_offset)

        last_update = bot.get_last_update()

        if last_update is None:
            sleep(1)
            continue

        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']
        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['chat']['first_name']

        last_chat_text_is_greeting = last_chat_text.lower() in greetings
        has_not_done_greeting = True #today == now.day

        if (states.get(last_chat_id) == 'iterating') and (last_chat_text.lower() == 'next'):
            if indexes[last_chat_id] < len(movies[last_chat_id]) - 1:
                indexes[last_chat_id] += 1
            else:
                pages[last_chat_id] += 1
                movies[last_chat_id] = ya.get_movies_by_genre(genres[last_chat_id], pages[last_chat_id])
                indexes[last_chat_id] = 0

            movie = ya.get_movie_by_header(movies[last_chat_id][indexes[last_chat_id]])

            bot.send_photo(last_chat_id, movie.poster)
            bot.send_message(last_chat_id, movie.title + '\n\n\n' + movie.description  + '\n\n\n' + movie.trailer)


            #bot.send_message(last_chat_id, movies[last_chat_id][indexes[last_chat_id]].title + '\n\n\n' + movies[last_chat_id][indexes[last_chat_id]].description)
            #bot.send_photo(last_chat_id, movies[last_chat_id][indexes[last_chat_id]].poster)

        elif states.get(last_chat_id) == 'genre':
            states[last_chat_id] = 'iterating'
            movies[last_chat_id] = ya.get_movies_by_genre(last_chat_text)
            indexes[last_chat_id] = 0
            pages[last_chat_id] = 1
            genres[last_chat_id] = last_chat_text


            movie = ya.get_movie_by_header(movies[last_chat_id][indexes[last_chat_id]])

            bot.send_photo(last_chat_id, movie.poster)
            bot.send_message(last_chat_id, movie.title + '\n\n\n' + movie.description  + '\n\n\n' + movie.trailer, reply_markup)



        elif (last_chat_text.lower() == '/genre'):
            states[last_chat_id] = 'genre'
            bot.send_message(last_chat_id, 'Пожалуйста, укажите желаемый жанр')

        elif last_chat_text_is_greeting and has_not_done_greeting and 6 <= hour <= 12:
            send_message(last_chat_id, "Доброе утро, {} !", last_chat_name)
            today += 1
        elif last_chat_text_is_greeting and has_not_done_greeting and 12 < hour <= 17:
            send_message(last_chat_id, "Добрый день, {} !", last_chat_name)
            today += 1
        elif last_chat_text_is_greeting and has_not_done_greeting and 17 < hour <= 23:
            send_message(last_chat_id, "Добрый вечер, {} !", last_chat_name)
            today += 1
        elif last_chat_text_is_greeting and has_not_done_greeting:
            send_message(last_chat_id, "Доброй ночи, {} !", last_chat_name)
            today += 1

        new_offset = last_update_id + 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
