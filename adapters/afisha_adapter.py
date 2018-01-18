import sys
import os
import datetime
import time

sys.path.append('../tools/')
sys.path.append('../resources/')
sys.path.append('../caching/')

from redis_connector import get_from_redis, write_to_redis, is_there_valid_schedule
from html_parcing import get_middle, remove_tags

import requests

from constants import actual_movies_page_size
from constants import scp_schedule_folder, scp_schedule_path
from constants import num_of_days_in_schedule, delay_between_request_sequence, redis_key_delimiter
from constants import msg_fetching_schedule, msg_counted_schedule_for

from collections import namedtuple

from scp_connector import send_file, read_file

from date_converting import to_unix, get_pretty_date

from file_operating import write_to_file

from message_manager import send_plain

MovieExtendedHeader = namedtuple('MovieExtendedHeader','title href id')

url = 'https://www.afisha.ru'

schedule_beginning = '<div class="b-theme-schedule">'
schedule_ending = '$("tr.s-tr-next3d").hover('

ml_part_beginning = '<div class="m-disp-table">'

ml_title_beginning = '<h3 class="usetags">'
ml_title_ending = '</h3>'

ml_id_beginning = "'https://www.afisha.ru/movie/"
ml_id_ending = '/'

#
#convert a piece of html code into a set of movie headers
#

def parse_movies_list(content, page):
    raw_movies_list = content.split(ml_part_beginning)

    movies_list = []

    for raw_movie in raw_movies_list[(page - 1) * actual_movies_page_size + 1 : page * actual_movies_page_size]:
        title = remove_tags(get_middle(raw_movie, ml_title_beginning, ml_title_ending)).replace('3D','')
        id = int(get_middle(raw_movie, ml_id_beginning, ml_id_ending))
        movies_list.append(MovieExtendedHeader(title, 'no href provided', id))

    return movies_list

#
#get set of headers of the actual movies by page
#

def get_actual_movies(page = 1):
    response = requests.get(url + '/spb/schedule_cinema/')

    content = str(response.content,'utf-8')

    movies_list = parse_movies_list(content, page)

    return movies_list

#
#extract from a piece of html code needed schedule
#

def parse_schedule(content):
    return get_middle(content, schedule_beginning, schedule_ending).replace('<script>','')

#
#make html file with schedule via movie's id, send it to the remote storage and return link
#

def make_html_schedule(id, bot = None, chat_id = None):

    href = scp_schedule_path + '/' + str(id) + ".html"

    if is_there_valid_schedule(id):
        return href

    if bot is not None:
        send_plain(bot = bot, chat_id = chat_id, message = msg_fetching_schedule)

    write_to_redis('schedule' + redis_key_delimiter + str(id), ' ', True)

    local_file_name = '../' + str(id) + ".html"
    remote_file_name = scp_schedule_folder + '/' + str(id) + ".html"

    today = datetime.datetime.now()
    schedule = ''
    for day_number in range(num_of_days_in_schedule):
        schedule += '<h1>' + get_pretty_date(to_unix(today)) + '</h1>'

        day_schedule_url = url + '/spb/schedule_cinema_product/' + str(id) + ('/%02i-%02i-%i/' % (today.day, today.month, today.year))

        response = requests.get(day_schedule_url)

        content = str(response.content,'utf-8')

        schedule += parse_schedule(content)

        if bot is not None:
            send_plain(bot = bot, chat_id = chat_id, message = msg_counted_schedule_for + get_pretty_date(to_unix(today)))

        print('day counted')

        today += datetime.timedelta(days=1)

        time.sleep(delay_between_request_sequence)

    write_to_file(schedule, local_file_name)

    send_file(local_file_name, remote_file_name)

    os.remove(local_file_name)

    return href

#print(get_actual_movies())
#print(make_html_schedule(230685))
#print(get_schedule(2018, 1, 10))
