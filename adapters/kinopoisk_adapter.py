from kinopoisk.movie import Movie
import requests
import re
import time
import html

import sys

sys.path.append("../tools/")

from html_parcing import remove_tags, get_middle

url = 'https://kinopoisk.ru'

part_beginning = '<p class="sub_title"'
head_beginning = '>'
head_ending = '<'
review_beginning = 'itemprop="reviewBody">'
review_ending = '</span>'

HEADERS = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,tg;q=0.6',
    'Connection':'keep-alive',
    'Cookie':'_ym_uid=15017664961052850810; yandexuid=534925761501766489; header_v2_popup_hidden=yes; my_perpages=%5B%5D; tickets_promo_popup_shown=1; PHPSESSID=1v4pjf2gj4eb3kgs4i5rsvn4j5; user_country=ru; yandex_gid=2; tc=2; mobile=no; _ym_isad=1; noflash=true; desktop_session_key=2aa1ff6214bd69f49034812a5fbd02ee53cac2b0e00be2aa329399546f6489edb234ea7688421a6e9cdba252f184feb28739907a9d63cb27f7adeb92db4206c7da8b74c32666eae10c14df3b2b455a51; desktop_session_key.sig=H1m2har3TF7aZUlItUknNTkfaKY; refresh_yandexuid=534925761501766489; spravka=dD0xNTE1MDgwNDE4O2k9MTc4LjEzMC43LjgzO3U9MTUxNTA4MDQxODUxNTM0MzA2ODtoPTM3NGRiZDJhODVhNmVlZmJlNjk5YzBjZDlhYzExYTU2; _ym_visorc_32993479=w; _ym_visorc_22663942=b; last_visit=2018-01-04+19%3A38%3A17; loc2=yes',
    'Host':'www.kinopoisk.ru',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.39 Safari/537.36',
}

description_beginning = '<span class="_reachbanner_"><div class="brand_words film-synopsys" itemprop="description">'
description_ending = '</div>'
title_beginning = '<h1 class="moviename-big" itemprop="name">'
title_ending = '</h1>'
poster_beginning = '<img width="205" src="'
poster_ending = '"'
year_beginning = '<td class="type">год</td>'

movie_attributes_beginning = {'country' : 'страна', 'slogan' : 'слоган', 'director' : 'режиссер',
                                'scenarist' : 'сценарий', 'producer' : 'продюсер', 'genre' : 'жанр', 'budget' : '<td class="type">бюджет',
                                 'MPAA rating' : 'рейтинг MPAA'}

movie_attributes_ending = {'genre' : '</td></tr>'}

movie_info_universal_ending = '</tr>'

def get_movie(title, year = None):
    movies = Movie.objects.search(title)
    for movie in movies:
        print(movie.title,movie.plot)

    if year == None:
        return movies[0]

    for movie in movies:
        if movie.year == int(year):
            return movie

def parse_reviews(page):
    raw_reviews = page.split(part_beginning)
    reviews = []
    for raw_review in raw_reviews[1:]:
        review = get_middle(raw_review, review_beginning, review_ending)
        title = html.unescape(get_middle(raw_review, head_beginning, head_ending))
        reviews.append(title + '\n\n' + remove_tags(review))
    return reviews

def parse_movie_info(content):
    result = {}
    #try:
    result['Description'] = html.unescape(get_middle(content, description_beginning, description_ending)).replace(u'\xa0',' ')
    #if len(content.split(year_beginning)) > 1:
    result['Title'] = remove_tags(html.unescape(get_middle(content, title_beginning, title_ending)).replace(u'\xa0',' ')) + ' (' + \
                        remove_tags(html.unescape(get_middle(content, year_beginning, movie_info_universal_ending)).replace(u'\xa0',' ')).lstrip().rstrip() + ')'
    #else:
        #result['Title'] = remove_tags(html.unescape(get_middle(content, title_beginning, title_ending)).replace(u'\xa0',' '))
    result['Poster'] = get_middle(content, poster_beginning, poster_ending)
    #except IndexError:
    #    pass
    for key in movie_attributes_beginning:
        try:
            if key not in movie_attributes_ending:
                result[key[0].upper()+key[1:]] = remove_tags(html.unescape(get_middle(content,
                                movie_attributes_beginning[key], movie_info_universal_ending))).lstrip().rstrip()
            else:
                result[key[0].upper()+key[1:]] = remove_tags(html.unescape(get_middle(content,
                                movie_attributes_beginning[key], movie_attributes_ending[key]))).lstrip().rstrip()
        except IndexError:
            pass
    return result

def get_movie_page_content(title):
    global url
    global HEADERS

    arr = title.split(' (')
    name = arr[0]
    if len(arr) > 1:
        year = arr[1].replace(')','').replace(' ','')
        movie = get_movie(name, year)
    else:
        movie = get_movie(name)

    if movie is None:
        return None

    response = requests.get(url + '/film/{}'.format(movie.id), headers = HEADERS)
    content = str(response.content, 'windows-1251', errors = 'ignore')
    return content

def get_reviews(title):
    content = get_movie_page_content(title)

    if content == None:
        return []

    reviews = parse_reviews(content)

    return reviews

def get_movie_info(title):
    content = get_movie_page_content(title)

    if content == None or content.find('Страница не найдена') >= 0:
        return None

    info = parse_movie_info(content.split('<!-- тривии -->')[0])
    return info

#print(get_movie_info('Теснота'))
