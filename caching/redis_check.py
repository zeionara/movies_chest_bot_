import redis
from collections import namedtuple
import pickle
import os

redis_host = os.environ['barbershop_redis_host']
redis_port = int(os.environ['barbershop_redis_port'])

redis_connection = redis.StrictRedis(host = redis_host, port = redis_port, db=0)

creation_time_prefix = 'creation'

def show_all():
    global creation_time_prefix

    for key in redis_connection.scan_iter():
        print(key)

def delete_all():
    global creation_time_prefix

    for key in redis_connection.scan_iter():
        redis_connection.delete(key)

delete_all()
#show_all()
#MovieHeader = namedtuple('MovieHeader','title href')
#redis_connection.set('mine_any_1', pickle.dumps([MovieHeader('The party (2017)', 'https://proxyspotting.in/torrent/19202259/The.Party.2017.BDRip.XviD.AC3-EVO'),
#                                                MovieHeader('Une femme douce (2017)', 'no href provided'),
#                                                MovieHeader('mother! (2017)', 'https://proxyspotting.in/torrent/19323252/Mother__(2017)_%5B1080p%5D_English'),
#                                                MovieHeader('Теснота (2017)', 'http://live-rutor.org/torrent/587125/tesnota-2017-web-dl-1080p-itunes/'),
#                                                MovieHeader('Три сестры (2017)', 'http://live-rutor.org/torrent/599389/tri-sestry-2017-webrip-720p'),
#                                                MovieHeader('The neon daemon (2016)', 'https://proxyspotting.in/torrent/15711131/The.Neon.Demon.2016.HDRip.XViD-ETRG'),
#                                                MovieHeader('Софичка (2016)', 'http://live-rutor.org/torrent/601473/sofichka-2016-web-dl-720p/'),
#                                                MovieHeader('Raw (2016)', 'https://proxyspotting.in/torrent/17062526/Nocturnal_Animals_2016_1080p_WEB-DL_x264_AC3-JYK'),
#                                                MovieHeader('Nocturnal animals (2016)', 'https://proxyspotting.in/torrent/17062526/Nocturnal_Animals_2016_1080p_WEB-DL_x264_AC3-JYK'),
#                                                MovieHeader('Into the forest (2015)', 'https://proxyspotting.in/torrent/15438683/Into.the.Forest.2015.HDRip.XviD.AC3-EVO')]))
#print(redis_connection.get('Jumanji: Welcome to the Jungle'))
