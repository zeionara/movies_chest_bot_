import sys
import os
import datetime
import time

sys.path.append('../tools/')
sys.path.append('../resources/')
sys.path.append('../caching/')

from redis_connector import get_from_redis, write_to_redis
from html_parcing import get_middle, remove_tags

import requests

from constants import actual_movies_page_size
from constants import scp_schedule_folder, scp_schedule_path
from constants import num_of_days_in_schedule, delay_between_request_sequence, redis_key_delimiter

from collections import namedtuple

from scp_connector import send_file, read_file

MovieExtendedHeader = namedtuple('MovieExtendedHeader','title href id')

url = 'https://www.afisha.ru'

schedule_beginning = '<div class="b-theme-schedule">'
schedule_ending = '$("tr.s-tr-next3d").hover('

ml_part_beginning = '<div class="m-disp-table">'

ml_title_beginning = '<h3 class="usetags">'
ml_title_ending = '</h3>'

ml_id_beginning = "'https://www.afisha.ru/movie/"
ml_id_ending = '/'

def is_there_valid_schedule(id):
    if get_from_redis('schedule' + redis_key_delimiter + str(id)) is None:
        return False
    return True

def parse_movies_list(content, page):
    raw_movies_list = content.split(ml_part_beginning)

    movies_list = []

    for raw_movie in raw_movies_list[(page - 1) * actual_movies_page_size + 1 : page * actual_movies_page_size]:
        title = remove_tags(get_middle(raw_movie, ml_title_beginning, ml_title_ending)).replace('3D','')
        id = int(get_middle(raw_movie, ml_id_beginning, ml_id_ending))
        movies_list.append(MovieExtendedHeader(title, 'no href provided', id))

    return movies_list

def get_actual_movies(page = 1):
    response = requests.get(url + '/spb/schedule_cinema/')

    content = str(response.content,'utf-8')

    movies_list = parse_movies_list(content, page)

    return movies_list

def parse_schedule(content):
    return get_middle(content, schedule_beginning, schedule_ending).replace('<script>','')

def write_to_file(text, file_name):
    with open(file_name, "w", encoding = 'utf8') as text_file:
        text_file.write(text)

def get_pretty_date(ugly_time):
	return datetime.datetime.fromtimestamp(int(ugly_time)).strftime('%d %B')

def to_unix(date_time):
    return time.mktime(date_time.timetuple())

def make_html_schedule(id, bot = None, chat_id = None):

    href = scp_schedule_path + '/' + str(id) + ".html"

    if is_there_valid_schedule(id):
        return href

    if bot is not None:
        bot.sendMessage(chat_id, 'Fetching schedule from website...')

    write_to_redis('schedule' + redis_key_delimiter + str(id), ' ', True)

    local_file_name = '../' + str(id) + ".html"
    remote_file_name = scp_schedule_folder + '/' + str(id) + ".html"

    today = datetime.datetime.now()
    schedule = ''
    for day_number in range(num_of_days_in_schedule):
        schedule += '<h1>' + get_pretty_date(to_unix(today)) + '</h1>'

        print(url + '/spb/schedule_cinema_product/' + str(id) + ('/%02i-%02i-%i/' % (today.year, today.month, today.day)))
        response = requests.get(url + '/spb/schedule_cinema_product/' + str(id) + ('/%02i-%02i-%i/' % (today.day, today.month, today.year)))

        content = str(response.content,'utf-8')

        schedule += parse_schedule(content)

        today += datetime.timedelta(days=1)

        print('day counted')

        time.sleep(delay_between_request_sequence)

    write_to_file(schedule, local_file_name)

    send_file(local_file_name, remote_file_name)

    os.remove(local_file_name)

    return href

#print(get_actual_movies())
#print(make_html_schedule(230685))
#print(get_schedule(2018, 1, 10))
