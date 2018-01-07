import requests
import re
import html

import sys

sys.path.append("../tools/")

from html_parcing import remove_tags, get_middle

url = 'https://www.rottentomatoes.com'
delimiter = '_'

def get_score(score_block):
    score = len(score_block.split('glyphicon glyphicon-star')) - 1
    if score_block.find('&frac12;') >= 0:
        score += 0.5
    return score

def parse_critics_reviews(page):
    raw_reviews = page.split('<div class="row review_table_row">')
    reviews = []
    for raw_review in raw_reviews[1:]:
        review = get_middle(raw_review,'<div class="the_review">','</div>')
        href = get_middle(raw_review.split('<a href="', maxsplit = 2)[2],'<a href="','"')
        author = get_middle(raw_review,'"unstyled bold articleLink">','<')
        try:
            score = get_middle(raw_review,'Score: ','<')
        except IndexError:
            score = 'n/a'

        review = 'Author: ' + author + '\n\nRated: ' + score + '\n\nFull review: ' + href + '\n\n' + review.lstrip()

        reviews.append(review)

    return reviews

def parse_audience_reviews(page):
    raw_reviews = page.split('<div class="row review_table_row">')
    reviews = []
    for raw_review in raw_reviews[1:]:
        review = get_middle(raw_review,'<div class="user_review" style="display:inline-block; width:100%">','</div> </div> </div>')
        score = get_score(get_middle(raw_review,'<span style="color:#F1870A" class="fl">','</span> <span class="fr small subtle">'))

        review = 'Rated: ' + str(score) + '/5\n\n' + remove_tags(review).lstrip()

        reviews.append(html.unescape(review))

    return reviews

def get_reviews_by_page_info(name, year, page, critics, include_year):
    if include_year:
        if critics:
            response = requests.get(url + '/m/{}_{}/reviews/?page={}&sort='.format(name, year, page))
        else:
            response = requests.get(url + '/m/{}_{}/reviews/?page={}&type=user'.format(name, year, page))
    else:
        if critics:
            response = requests.get(url + '/m/{}/reviews/?page={}&sort='.format(name, page))
        else:
            response = requests.get(url + '/m/{}/reviews/?page={}&type=user'.format(name, page))

    content = str(response.content)

    if critics:
        reviews = parse_critics_reviews(content)
    else:
        reviews = parse_audience_reviews(content)

    return reviews

def get_reviews(title, critics = True, page = 1):
    global url

    arr = title.split(' (')
    name = arr[0].replace(' ',delimiter).lower().replace('-','_')
    year = arr[1].replace(')','').replace(' ','')

    reviews = get_reviews_by_page_info(name, year, page, critics, False)
    if len(reviews) == 0:
        reviews = get_reviews_by_page_info(name, year, page, critics, True)

    return reviews

def get_critics_reviews_from_rotten_tomatoes(title, page = 1):
    return get_reviews(title, True, page)

def get_audience_reviews_from_rotten_tomatoes(title, page = 1):
    return get_reviews(title, False, page)

#reviews = get_reviews('Geostorm (2017)', critics = False)
#for review in reviews:
#    print(review)
