import datetime
import time

def get_pretty_date(ugly_time):
	return datetime.datetime.fromtimestamp(int(ugly_time)).strftime('%d %B')

def to_unix(date_time):
    return time.mktime(date_time.timetuple())
