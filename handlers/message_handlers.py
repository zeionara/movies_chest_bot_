import sys
import traceback

from shared import users

from movies_manager import send_advanced_single_movie_info
from movies_manager import get_advanced_movie_info_by_title

from subscriptions_manager import register_subscription

from constants import states
from constants import tracker_names_delimiter
from constants import tracker_names
from constants import genres_lower
from constants import trackers
from constants import msg_choose_genre_to_subscripe, any_keyword

from keyboard_markups import yes_no_reply_markup

def handle_subscription_request(bot, update):
    print('fuvk')
    try:
        chat_id = update['message']['chat']['id']
        objs = update['message']['text']

        print('state: ',users[chat_id].state)
        if users.get(chat_id) is not None and users[chat_id].state == states['choosing_tracker_to_subscribe']:
             #send_advanced_single_movie_info(bot, chat_id, get_advanced_movie_info_by_title(title))
             selected_trackers = []
             selected_tracker_names = objs.split(tracker_names_delimiter)
             if any_keyword in selected_tracker_names:
                 for tracker in trackers:
                     selected_trackers.append(tracker)
             else:
                 for tracker_name in selected_tracker_names:
                     tracker_name = tracker_name.replace(' ','')
                     if not (tracker_name in tracker_names):
                        print('Error in tracker')
                        bot.sendMessage(chat_id = chat_id, text = 'Oops, it seems that you entered something wrong. Do you want to try again?',
                                        reply_markup = yes_no_reply_markup)
                        #users[chat_id].state = states['undefined']
                        return
                     selected_trackers.append(trackers[tracker_names.index(tracker_name)])
             print('state bef: ',users[chat_id].state)
             print('set to ', states['choosing_genre_to_subscribe'])
             users[chat_id].state = states['choosing_genre_to_subscribe']
             users[chat_id].trackers_to_subscribe = selected_trackers
             print('state after: ',users[chat_id].state)
             response = bot.sendMessage(chat_id = chat_id, text = msg_choose_genre_to_subscripe + tracker_names_delimiter.join(genres_lower))
             return response

        elif users.get(chat_id) is not None and users[chat_id].state == states['choosing_genre_to_subscribe']:
             #send_advanced_single_movie_info(bot, chat_id, get_advanced_movie_info_by_title(title))
             selected_genres = objs.split(tracker_names_delimiter)
             print(selected_genres)
             if any_keyword in selected_genres:
                 selected_genres = []
                 for genre in genres_lower:
                     selected_genres.append(genre)
             else:
                 for genre in selected_genres:
                     genre = genre.replace(' ','')
                     print(genre)
                     if not (genre in genres_lower):
                        print('Error in genre')
                        bot.sendMessage(chat_id = chat_id, text = 'Oops, it seems that you entered something wrong. Do you want to try again?',
                                        reply_markup = yes_no_reply_markup)
                        #users[chat_id].state = states['undefined']
                        return

             users[chat_id].state = states['undefined']
             response = bot.sendMessage(chat_id = chat_id, text = 'success!')
             print(selected_genres)
             print(users[chat_id].trackers_to_subscribe)
             register_subscription(chat_id, users[chat_id].trackers_to_subscribe, selected_genres)
             return response


    except Exception:
        print(sys.exc_info()[1])
        print(traceback.print_tb(sys.exc_info()[2]))

def handle_movie_request(bot, update):
    print('ssss')
    try:
        chat_id = update['message']['chat']['id']
        title = update['message']['text']

        if users.get(chat_id) is not None and users[chat_id].state == states['searching']:
             send_advanced_single_movie_info(bot, chat_id, get_advanced_movie_info_by_title(title))

             users[chat_id].state = states['undefined']
        else:
            handle_subscription_request(bot, update)
    except Exception:
        print(sys.exc_info()[1])
        print(traceback.print_tb(sys.exc_info()[2]))
