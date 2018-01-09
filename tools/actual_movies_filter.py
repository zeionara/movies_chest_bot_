#import sys
#sys.path.append('../resources/')
# -*- coding: utf-8 -*-
#import datetime
import shared

import constants
from constants import interesting_cinemas
from constants import cinemas_indexes
from constants import cinemas_query_part
from constants import seconds_in_day
from constants import scp_schedule_folder, scp_schedule_path
from constants import num_of_days_in_schedule, delay_between_request_sequence

from collections import namedtuple

import mirage_cinema_adapter
import kinopik_adapter

import time

import datetime

import requests

from scp_connector import send_file, read_file

MovieExtendedHeader = namedtuple('MovieExtendedHeader','title href id schedule')

def cut_title(title):
    return title.split(' (')[0].lstrip().rstrip()

def update_cinemas_data():
	response = requests.get('https://kudago.com/public-api/v1.3/places/?categories=cinema&location=spb&fields=title,id&page_size=100')
	result = []
	cinemas_query_part = ''

	for cinema in response.json()['results']:
		for interesting_cinema in interesting_cinemas:
			if cinema['title'].lstrip().lower().find(interesting_cinema) >= 0:
				cinemas_indexes[cinema['id']] = cinema['title']

	for cinema_index in cinemas_indexes:
		constants.cinemas_query_part += '&place=' + str(cinema_index)

def get_cinemas_query_part():
	#print(constants.cinemas_query_part)
	if constants.cinemas_query_part == '':
		update_cinemas_data()
	return constants.cinemas_query_part

def get_pretty_time(ugly_time):
	return datetime.datetime.fromtimestamp(int(ugly_time)).strftime('%d %B %H:%M:%S')

def get_pretty_date(ugly_time):
	return datetime.datetime.fromtimestamp(int(ugly_time)).strftime('%d %B')

def to_unix(date_time):
    return time.mktime(date_time.timetuple())

def get_whole_schedule():
	if shared.whole_schedule is None:
		shared.whole_schedule = {}
		today = datetime.datetime.now()
		for day_number in range(num_of_days_in_schedule):
			shared.whole_schedule[to_unix(today)] = {}
			shared.whole_schedule[to_unix(today)]['Mirage cinema'] = mirage_cinema_adapter.get_schedule(today.year, today.month, today.day)
			shared.whole_schedule[to_unix(today)]['Kinopik'] = kinopik_adapter.get_schedule(today.year, today.month, today.day)
			today += datetime.timedelta(days=1)
			print('day counted')
			time.sleep(delay_between_request_sequence)
	return shared.whole_schedule

def get_movie_today_schedule(title):
	title = cut_title(title)
	whole_schedule = get_whole_schedule()
	result = ''
	for cinema in whole_schedule:
		if title in whole_schedule[cinema]:
			result += cinema + '\n'
			for seance in whole_schedule[cinema][title]:
				result += ('\t%-32s\t%-15s\t%-4s\n' % (seance['location'], seance['time'], seance['price']))
	return result

def save_movie_today_schedule(title):

	local_file_name = '../'+title+".html"
	remote_file_name = scp_schedule_folder + '/' + title+".html"
	href = scp_schedule_path + '/' + title+".html"

	if read_file(remote_file_name):
		return href

	current_time = int(time.time())

	title = cut_title(title)
	whole_schedule = get_whole_schedule()
	result = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head><body>'
	for date in whole_schedule:
		result += '<div><h1>' + get_pretty_date(date) + '</h1><table>'
		#print(date)
		for cinema in whole_schedule[date]:
			#print('for ',cinema,' : ',whole_schedule[date][cinema])
			if title in whole_schedule[date][cinema]:
				result += '<tr><td><h2>' + cinema + '<h2></td></tr>'
				for seance in whole_schedule[date][cinema][title]:
					result += ('<td>%s</td><td>%s</td><td>%s</td></tr>' % (seance['location'], seance['time'], seance['price']))
		result += '</table></div>'
	result += '</body></html>'

	with open(local_file_name, "w", encoding = 'utf8') as text_file:
		text_file.write(result)

	send_file(local_file_name, remote_file_name)

	return href

def get_movie_schedule(id, days_before, days_after):
	current_time = int(time.time())

	url = ('https://kudago.com/public-api/v1.3/movies/{}/showings/?location=spb&actual_since={}&actual_until={}'+get_cinemas_query_part()).format(id,
			current_time - days_before*seconds_in_day, current_time + days_after*seconds_in_day)

	print(url)

	response = requests.get(url)

	print(cinemas_indexes)

	for showing in response.json()['results']:
		if showing['place']['id'] in cinemas_indexes:
			#print(showing)
			print(cinemas_indexes[showing['place']['id']])
			print(get_pretty_time(showing['datetime']))
		else:
			print(showing['place']['id'])

def stringify_schedule(raw_schedule):
	result = ''
	for cinema in raw_schedule:
		result += cinema + '\n'
		for showing_time in raw_schedule[cinema]:
			result += '\t' + showing_time + '\n'
		result += '\n\n'
	return result

def check_actual_movies(movies, days_before, days_after):
	current_time = int(time.time())

	url_beginning = 'https://kudago.com/public-api/v1.3/movies/'
	url_ending = ('/showings/?location=spb&actual_since={}&actual_until={}'+get_cinemas_query_part()).format(
			current_time - days_before*seconds_in_day, current_time + days_after*seconds_in_day)

	for movie in movies:
		id = movie.id
		url = url_beginning + str(id) + url_ending

		response = requests.get(url)
		valid = False

		raw_schedule = {}

		for showing in response.json()['results']:
			place_id = showing['place']['id']
			if place_id in cinemas_indexes:
				if not valid:
					valid = True

				cinema_name = cinemas_indexes[place_id]
				#print(showing['datetime'])
				showing_time = get_pretty_time(int(showing['datetime']))

				if cinema_name not in raw_schedule:
					raw_schedule[cinema_name] = [showing_time]
				else:
					raw_schedule[cinema_name].append(showing_time)

		if valid:
			print(stringify_schedule(raw_schedule))
			print(movie)


	#print(cinemas_indexes)



#print(get_cinemas_query_part())
