import os
import credentials
import json

DEBUG_MODE = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
LOG_LEVEL = int(os.environ.get('LOG_LEVEL', 20))

FLOWROUTE_SECRET_KEY = os.environ.get('FLOWROUTE_SECRET_KEY',
                                      credentials.FLOWROUTE_SECRET_KEY)
FLOWROUTE_ACCESS_KEY = os.environ.get('FLOWROUTE_ACCESS_KEY',
                                      credentials.FLOWROUTE_ACCESS_KEY)
POLL_NUMBER = os.environ.get('POLL_NUMBER', credentials.FLOWROUTE_NUMBER)
ids = os.environ.get('HACK_IDS', None)
if ids is None:
    HACK_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
else:
    HACK_IDS = json.loads(ids)
HEADER = os.environ.get('HEADER', 'ClueCon 2016')

TEST_DB = "test_sms_vote.db"
DB = "sms_vote.db"
