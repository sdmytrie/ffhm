import os

URL = "toto"
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TOKEN_FILE = os.path.join(os.path.dirname(BASE_DIR), 'exalto', 'data', 'token.json')
TOKEN_LOGIN = "scoresheetapi"
TOKEN_PASSWORD = "XXX"
TOKEN_URL = "https://intranet.ffhaltero.fr/api/v1/login"

MONGO_URI = "mongodb://localhost:27017"

from .settings import *
