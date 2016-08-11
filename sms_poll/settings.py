import os

DEBUG_MODE = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
LOG_LEVEL = int(os.environ.get('LOG_LEVEL', 30))

FLOWROUTE_SECRET_KEY = os.environ.get('FLOWROUTE_SECRET_KEY', None)
FLOWROUTE_ACCESS_KEY = os.environ.get('FLOWROUTE_ACCESS_KEY', None)

POLL_NUMBER = os.environ.get('POLL_NUMBER')
HACK_IDS = os.environ.get('HACK_IDS')
HEADER = os.environ.get('HEADER', 'ClueCon 2016')

TEST_DB = "test_sms_vote.db"
DB = "sms_vote.db"
