import sys

sys.path.append('../tools/')

from html_parcing import get_middle, remove_tags

import requests

url = 'http://www.mirage.ru'

part_beginning = '<td class="col1">'
time_beginning = '<b>'
time_ending = '</td>'
title_beginning = 'class="red">'
title_ending = '</a>'
location_beginning = '</a>">'
location_ending = '</a>'
price_beginning = '<span class="price-data">'
price_ending = '</span>'

def parse_schedule(content):
    raw_schedule = content.split(part_beginning)
    schedule = {}

    for item in raw_schedule[1:]:
        time = remove_tags(get_middle(item, time_beginning, time_ending)).lstrip().rstrip()
        title = remove_tags(get_middle(item, title_beginning, title_ending)).replace('3D','').replace('Dolby Atmos','').lstrip().rstrip()
        location = ' '.join([location_part.lstrip().rstrip() for location_part in \
                        remove_tags(get_middle(item, location_beginning, location_ending)).lstrip().rstrip().split('\n')]).replace('«Мираж Синема» в','').replace('«Мираж Синема» на','')
        price = get_middle(item, price_beginning, price_ending)

        if title not in schedule:
            schedule[title] = [{'time' : time, 'location' : location, 'price' : price}]
        else:
            schedule[title].append({'time' : time, 'location' : location, 'price' : price})

    return schedule

def get_schedule(year = None, month = None, day = None):
    if day == None or month == None or year == None:
        response = requests.get(url + '/schedule/raspisanie.htm')
    else:
        response = requests.get(url + '/schedule/%i%02i%02i/0/0/0/0/0/raspisanie.htm' % (year, month, day))

    content = str(response.content,'utf-8')

    schedule = parse_schedule(content)

    return schedule

#print(get_schedule(2018, 1, 10))
