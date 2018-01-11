import requests
from collections import namedtuple
import re

import sys

sys.path.append("../tools/")

from html_parcing import get_middle, delete_slashes

Movie = namedtuple('Movie','title poster description trailer')
MovieHeader = namedtuple('MovieHeader','title href')

class PiratebayAdapter:

    def __init__(self):
        self.url = 'https://proxyspotting.in'

    def get_title(self, movie_raw):
        raw_title = get_middle(movie_raw, 'title="', '"').replace('Details for ','')

        square_bracket_index = raw_title.find(']')

        if square_bracket_index is not None:
            raw_title = raw_title[square_bracket_index + 1:]

        found_years = re.findall('19[0-9]{2}|20[0-9]{2}',raw_title)

        if type(found_years[-1]) != type('ok'):
            year = found_years[-1][0]
        else:
            year = found_years[-1]

        year_index = raw_title.find(year)
        delimiter = raw_title[year_index - 1]

        if delimiter != '(':
            splitted_raw_title = raw_title.replace('.',delimiter).replace(' ',delimiter).split(delimiter)
            title = ' '.join(splitted_raw_title[:splitted_raw_title.index(year)]) + ' (' + year + ')'
        else:
            title = raw_title[:raw_title.index('(') + len(year) + 1] + ')'

        return delete_slashes(title.lstrip())

    def get_href(self, movie_raw):
        return get_middle(movie_raw, 'href="', '"')

    def rreduce(self, title):
        return (''.join(e for e in title if e.isalnum())).lower()

    def get_movies(self, section_raw):
        movie_reduced_titles = []
        movie_titles_raw = section_raw.split('<div class="detName">')[1:]
        movies = []
        movie_headers = []
        movie_reduced_headers = []

        for movie_title_raw in movie_titles_raw:
            try:
                title = self.get_title(movie_title_raw)
                href = self.get_href(movie_title_raw)
            except Exception as e:
                print(e)
                continue

            movie_reduced_title = self.rreduce(title)

            if movie_reduced_title not in movie_reduced_titles:
                print(title)
                movie_header = MovieHeader(title, href)
                movie_headers.append(movie_header)
                movie_reduced_titles.append(movie_reduced_title)

        #print(movie_headers)
        #print('............................................')
        #print(movie_reduced_headers)
        return movie_headers

    def get_movies_by_page(self, page = 1):

        response = requests.get(self.url + '/browse/201/{}/3'.format(page - 1))
        content = str(response.content)

        movies = self.get_movies(content)
        return movies


#pa = PiratebayAdapter()
#print(pa.get_movies_by_page())
