import sys

sys.path.append('../tools/')

from html_parcing import get_middle, remove_tags

import requests

#afisha-seance-wrapper block-

url = 'https://kinopik.info'

part_beginning = 'afisha-list-item filter-block'
time_beginning = '&quot;:&quot;18&quot;,&quot;marketId&quot;:&quot;1472&quot;}); return false;">'
time_ending = '</a>'
title_beginning = 'class="film-title">'
title_ending = '</a>'
location_beginning = '<lh>'
location_ending = '</lh>'
price_beginning = '<span class="price-value">'
price_ending = '</span>'

def parse_schedule(content):
    raw_schedule = content.split(part_beginning)
    schedule = {}

    for item in raw_schedule[1:]:
        #time = remove_tags(get_middle(item, time_beginning, time_ending)).lstrip().rstrip()
        title = remove_tags(get_middle(item, title_beginning, title_ending)).replace('3D','').replace('Dolby Atmos','').lstrip().rstrip()
        print(title)

        local_result = []

        for location_raw in item.split(location_beginning)[1:]:
            location = location_raw.split(location_ending)[0]

            times = []
            prices = []

            for time_raw in location_raw.split(time_beginning)[1:]:
                times.append(time_raw.split(time_ending)[0])

            for price_raw in location_raw.split(price_beginning)[1:]:
                prices.append(price_raw.split(price_ending)[0])

            for i in range(len(prices)):
                local_result.append({'time' : times[i], 'location' : location, 'price' : prices[i]})

        schedule[title] = local_result

    return schedule

def get_schedule(year = None, month = None, day = None):
    if day == None or month == None or year == None:
        response = requests.get(url + '/#afisha')
    else:
        response = requests.get(url + '/?schedule_date=%i-%02i-%02i#afisha' % (year, month, day))

    content = str(response.content,'utf-8')

    schedule = parse_schedule(content)

    return schedule

#print(get_schedule(2018, 1, 14))
