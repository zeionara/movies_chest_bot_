from collections import namedtuple

MovieHeader = namedtuple('MovieHeader','title href')
MovieExtendedHeader = namedtuple('MovieExtendedHeader','title href id')

def list_to_movie_header(movie_list):
    if len(movie_list) == 2:
        return MovieHeader(*movie_list)
    elif len(movie_list) == 3:
        return MovieExtendedHeader(*movie_list)
