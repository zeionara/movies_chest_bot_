from constants import delimiter
from constants import forbidden_movie_fields

def join(*args):
    return delimiter.join(args)

def split(string, maxsplit = None):
    if maxsplit is None:
        return string.split(delimiter)
    else:
        return string.split(delimiter, maxsplit = maxsplit)

def chunkstring(string):
    return [string[0+i:max_message_length+i] for i in range(0, len(string), max_message_length)]

def stringify_advanced_movie_info(info):
    result = ''

    if 'Trailer' in info:
        result += 'Trailer : ' + info['Trailer'] + '\n\n'

    for item in info:
        if item not in forbidden_movie_fields and type(info.get(item)) == type('ok') and info.get(item) != 'N/A':
            result += item + ' : ' + info[item] + '\n\n'

    return result
