import xml.etree.ElementTree as ET
from collections import namedtuple

default_path = '../resources/top_movies.xml'

MovieHeader = namedtuple('MovieHeader','title href')

def get_top_movies(path = None):
    global default_path

    if path is None:
        path = default_path
    
    tree = ET.parse(path)
    root = tree.getroot()
    result = []
    for movie in root.iter('movie'):
        result.append(MovieHeader(movie.find('title').text, movie.find('href').text))
    return result

#print(get_top_movies())
