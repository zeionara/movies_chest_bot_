import sys
import traceback

from shared import users

from movies_manager import send_advanced_single_movie_info
from movies_manager import get_advanced_movie_info_by_title

from subscriptions_manager import register_subscription, unregister_subscription

from constants import states
from constants import tracker_names_delimiter
from constants import tracker_names
from constants import genres_lower
from constants import trackers
from constants import msg_choose_genre_to_subscripe, any_keyword, genred_trackers, msg_choose_genre_to_unsubscripe, msg_entered_wrong

from keyboard_markups import yes_no_reply_markup

from threading import Thread

from subscriptions_manager import get_subscribed_genres

def handle_subscription_request(bot, update):
    print('fuvk')
    try:
        chat_id = update['message']['chat']['id']
        objs = update['message']['text']

        print('state: ',users[chat_id].state)
        if users.get(chat_id) is not None and (users[chat_id].state == states['choosing_tracker_to_subscribe']\
                                                or users[chat_id].state == states['choosing_tracker_to_unsubscribe']):
             genred = False
             #send_advanced_single_movie_info(bot, chat_id, get_advanced_movie_info_by_title(title))
             selected_trackers = []
             selected_tracker_names = [tracker_name.lstrip().rstrip() for tracker_name in objs.split(tracker_names_delimiter)]

             if users[chat_id].state == states['choosing_tracker_to_subscribe']:
                 actual_tracker_names = [tracker for tracker in tracker_names]
             elif users[chat_id].state == states['choosing_tracker_to_unsubscribe']:
                 actual_tracker_names = [tracker for tracker in users[chat_id].tmp]

             if any_keyword in selected_tracker_names:
                 selected_tracker_names = []
                 for tracker_name in actual_tracker_names:
                     selected_trackers.append(tracker_name)
                     #genred = True
             #else:
             for tracker_name in selected_tracker_names:
                 print(tracker_name)
                 print(actual_tracker_names)
                 #tracker_name = tracker_name.lstrip().rstrip()
                 if not (tracker_name in actual_tracker_names):
                     print('Error in tracker')
                     bot.sendMessage(chat_id = chat_id, text = msg_entered_wrong, reply_markup = yes_no_reply_markup)
                        #users[chat_id].state = states['undefined']
                     return
                 if trackers[tracker_names.index(tracker_name)] in genred_trackers:
                     genred = True
                 selected_trackers.append(trackers[tracker_names.index(tracker_name)])
             print('state bef: ',users[chat_id].state)
             print('set to ', states['choosing_genre_to_subscribe'])
             if users[chat_id].state == states['choosing_tracker_to_subscribe']:
                 users[chat_id].state = states['choosing_genre_to_subscribe']
             elif users[chat_id].state == states['choosing_tracker_to_unsubscribe']:
                 users[chat_id].state = states['choosing_genre_to_unsubscribe']
             users[chat_id].trackers_to_subscribe = selected_trackers
             print('state after: ',users[chat_id].state)
             if not genred:

                 response = bot.sendMessage(chat_id = chat_id, text = 'success!')
                 if users[chat_id].state == states['choosing_genre_to_subscribe']:
                     #register_subscription(chat_id, selected_trackers, ['any'])
                     thread = Thread(target = register_subscription, args = (chat_id, users[chat_id].trackers_to_subscribe, ['any']))
                     thread.start()
                 elif users[chat_id].state == states['choosing_genre_to_unsubscribe']:
                     thread = Thread(target = unregister_subscription, args = (chat_id, users[chat_id].trackers_to_subscribe, ['any']))
                     thread.start()

                 users[chat_id].state = states['undefined']
                 return
             if users[chat_id].state == states['choosing_genre_to_subscribe']:
                 response = bot.sendMessage(chat_id = chat_id, text = msg_choose_genre_to_subscripe + (tracker_names_delimiter+' ').join(genres_lower))
             elif users[chat_id].state == states['choosing_genre_to_unsubscribe']:
                 subscribed_genres = get_subscribed_genres(chat_id)
                 users[chat_id].tmp = subscribed_genres
                 response = bot.sendMessage(chat_id = chat_id, text = msg_choose_genre_to_unsubscripe + (tracker_names_delimiter+' ').join(subscribed_genres))
             return response

        elif users.get(chat_id) is not None and (users[chat_id].state == states['choosing_genre_to_subscribe'] \
                                                or users[chat_id].state == states['choosing_genre_to_unsubscribe']):
             #send_advanced_single_movie_info(bot, chat_id, get_advanced_movie_info_by_title(title))
             selected_genres = [genre.lstrip().rstrip() for genre in objs.split(tracker_names_delimiter)]

             if users[chat_id].state == states['choosing_genre_to_subscribe']:
                 actual_genres = [genre for genre in genres_lower]
             elif users[chat_id].state == states['choosing_genre_to_unsubscribe']:
                 actual_genres = [genre for genre in users[chat_id].tmp]

             print(selected_genres)
             if any_keyword in selected_genres:
                 selected_genres = []
                 for genre in actual_genres:
                     selected_genres.append(genre)
             else:
                 for genre in selected_genres:
                     #genre = genre.lstrip().rstrip()
                     print(genre)
                     if not (genre in actual_genres):
                        print('Error in genre')
                        bot.sendMessage(chat_id = chat_id, text = msg_entered_wrong,
                                        reply_markup = yes_no_reply_markup)
                        #users[chat_id].state = states['undefined']
                        return


             response = bot.sendMessage(chat_id = chat_id, text = 'success!')
             print(selected_genres)
             print(users[chat_id].trackers_to_subscribe)

             if users[chat_id].state == states['choosing_genre_to_subscribe']:
                 thread = Thread(target = register_subscription, args = (chat_id, users[chat_id].trackers_to_subscribe, selected_genres))
                 thread.start()

             elif users[chat_id].state == states['choosing_genre_to_unsubscribe']:
                 thread = Thread(target = unregister_subscription, args = (chat_id, users[chat_id].trackers_to_subscribe, selected_genres))
                 thread.start()

             users[chat_id].state = states['undefined']

             #register_subscription(chat_id, users[chat_id].trackers_to_subscribe, selected_genres)
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
