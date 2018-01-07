import requests
from collections import namedtuple

class YuptorrentsAdapter:

    def get_middle(self, string, left_part, right_part):
        return string.split(left_part)[1].split(right_part)[0]

    def get_title(self, movie_raw):
        return self.get_middle(movie_raw, '<a title="', '"').replace('Download ','')

    def get_href(self, movie_raw):
        return self.get_middle(movie_raw, 'href="', '"')

    def get_youtube_href(self, movie_page):
        return self.get_middle(movie_page, '<iframe width="100%" height="300px" src="', '"').replace('embed/','').replace('be.com','.be').replace('www.','')

    def get_poster_href(self, movie_page):
        return self.url + '/' + movie_page.split('id="cover" src="')[2].split('"')[0]

    def get_description(self, movie_page):
        return self.get_middle(movie_page, '</h2>', '</p>').split(': ', maxsplit = 1)[1].replace('\\','')

    def __init__(self):
        self.url = 'https://yuptorrents.com'
        self.Movie = namedtuple('Movie','title poster description trailer')
        self.MovieHeader = namedtuple('Movie','title href')

    def movies_to_string(self, movies):
        result = ''
        for movie in movies:
            result += 'Title: {}\n\nPoster: {}\n\nDescription: {}\n\nTrailer: {}\n\n\n'.format(movie.title,
                movie.poster, movie.description, movie.trailer)
        return result

    def get_movies(self, section_raw):

        movie_titles_raw = section_raw.split('col-md-2 item top-padding">')[1:-1]
        movies = []
        movie_headers = []

        for movie_title_raw in movie_titles_raw:
            title = self.get_title(movie_title_raw)
            href = self.get_href(movie_title_raw)

            print(title)

            movie_header = self.MovieHeader(title, href)
            movie_headers.append(movie_header)


            #movie_response = requests.get(href)
            #movie_page = str(movie_response.content)
            #youtube_href = self.get_youtube_href(movie_page)
            #description = self.get_description(movie_page)
            #poster = self.get_poster_href(movie_page)

            #movie = self.Movie(title, poster, description, youtube_href)
            #movies.append(movie)

        return movie_headers

    def get_movie_by_header(self, movie_header):

        movie_response = requests.get(movie_header.href)
        movie_page = str(movie_response.content)

        youtube_href = self.get_youtube_href(movie_page)
        description = self.get_description(movie_page)
        poster = self.get_poster_href(movie_page)

        movie = self.Movie(movie_header.title, poster, description, youtube_href)
        return movie

    def get_movies_by_section(self, section_name):
        response = requests.get(self.url)
        page = str(response.content)

        section_raw = page.split('{}</a>'.format(section_name))[1].split('container-fluid top-padding')[0]
        movies = self.get_movies(section_raw)
        return movies

    def get_movies_by_genre(self, genre, page = 1):
        params = {'genre': genre, 'page': page}

        response = requests.get(self.url + '/browse?genre={}&page={}'.format(genre, page))
        page = str(response.content)

        movies = self.get_movies(page)
        return movies


#ya = YuptorrentsAdapter()
#print(ya.get_movies_by_section('Popular'))
