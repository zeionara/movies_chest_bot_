import requests
import re

import logging

import sys

sys.path.append("../tools/")

from html_parcing import remove_tags, get_middle

url = 'http://imdb.com'

part_beginning = '<span class="rating-other-user-rating">'
review_beginning = '<div class="text">'
review_ending = '</div>'
title_beginning = '<div class="title">'
title_ending = '</div>'
score_beginning = '<span>'
score_ending = '</span>'
spoiler_sign = 'spoiler-warning__control ipl-expander__control'

def parse_reviews(page):
    raw_reviews = page.split(part_beginning)
    reviews = []
    for raw_review in raw_reviews[1:]:
        review = remove_tags(get_middle(raw_review, review_beginning, review_ending))
        title = remove_tags(get_middle(raw_review, title_beginning, title_ending))
        score = get_middle(raw_review, score_beginning, score_ending)
        if len(raw_review.split(spoiler_sign)) > 2:
            review = "SPOILERS!!!!!!!\n\n" + title + '\n\n' + 'Rated: ' + score + '\n\n' + review
        else:
            review = title + '\n\n' + 'Rated: ' + score + '\n\n' + review
        reviews.append(remove_tags(review))
    return reviews

def get_reviews(id_):
    global url

    logging.info('Url reviews: {}'.format(url + '/title/{}/reviews'.format(id_)))
    response = requests.get(url + '/title/{}/reviews'.format(id_))
    content = str(response.content)

    reviews = parse_reviews(content)
    logging.info('Got reviews: {}'.format(reviews))
    return reviews

#print(get_reviews('tt5208216'))
