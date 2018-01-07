import os

delimiter = '_'
redis_key_delimiter = '_'
time_prefix = 'time'
creation_time_prefix = 'creation'
reviews_prefix = 'reviews'
buttons_per_string_in_wiki_markup = 2
buttons_per_string_in_genres_markup = 3
max_message_length = 1500
top_movies_xml_path = 'resources/top_movies.xml'

delay_between_request_sequence = 5

any_keyword = 'any'
first_page = 1

max_lifetime = 3600
max_memory = 50240
checking_interval = 3600

states = {'selecting_tracker' : 0, 'selecting_genre' : 1, 'iterating' : 2, 'searching' : 3, 'undefined' : 4, 'choosing_tracker_to_subscribe': 5,
            'choosing_genre_to_subscribe': 6}
genres = ['Action','Crime','Thriller','Drama','Fantasy','Romance','Adventure','Comedy','Documentary',
        'Biography','Horror','Family','Sci-Fi','War','Mystery','History','Sport','Music','Western','Animation','Superhero']
genres_lower = ['action','crime','thriller','drama','fantasy','romance','adventure','comedy','documentary',
        'biography','horror','family','sci-fi','war','mystery','history','sport','music','western','animation','superhero']
trackers = ['yup', 'pbay', 'mine', 'act']
genred_trackers = ['yup','act']
tracker_names = ['yuptorrents', 'piratebay', 'gold collection', 'actual movies']
tracker_names_delimiter = ','

forbidden_movie_fields = ['Response', 'Poster', 'Type', 'imdbID', 'Title', 'Trailer']

msg_tracker_is_not_set = 'Tracker is not set, please, select it at first'
msg_invalid_command_for_tracker = 'Unsupported operation for the selected tracker'
msg_choose_genre = 'Please choose a genre:'
msg_choose_tracker = 'Please choose a tracker:'
msg_send_me_title_for_search = 'Please send me the title of the searched movie and the year in format: "The Beguiled (2017)"'
msg_genre_is_not_set = 'Genre is not selected, please, set it at first'
msg_coming_soon = 'The feature is coming soon'
msg_choose_tracker_to_subscripe = 'Please, send me a list of trackers which you want to send you notifications, for separating them use "' +\
            tracker_names_delimiter + '". If you want to get notifications from any tracker, just write "any". Available partial options are: '
msg_choose_genre_to_subscripe = 'Please, send me a list of genres which you want to keep an eye, for separating them use "' +\
            tracker_names_delimiter + '". If you want to get notifications for any genre, just write "any". Available partial options are: '

omdb_api_key = os.environ['zeionara_omdb_api_key']
redis_host = os.environ['barbershop_redis_host']
redis_port = int(os.environ['barbershop_redis_port'])
telegram_token = os.environ['movies_chest_bot_token']
developer_key = os.environ['zeionara_google_developer_key']
