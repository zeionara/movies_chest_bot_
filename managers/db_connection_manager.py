import sys
sys.path.append('../resources/')

from ming import create_datastore
from ming.odm import ThreadLocalODMSession

from constants import db_login, db_password, db_path

session = None

#
#get existing db session, if there is no one, then create it
#

def get_session():
    global session
    if session == None:
        session = ThreadLocalODMSession(bind = create_datastore('mongodb://%s:%s@%s' % (db_login, db_password, db_path)))
    return session
