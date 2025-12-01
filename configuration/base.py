import os

from dotenv import load_dotenv

load_dotenv()

MAX_CONNECTIONS = int(os.getenv('MAX_CONNECTIONS'))
MIN_CONNECTIONS = int(os.getenv('MIN_CONNECTIONS'))
LIFE_TIME = int(os.getenv('LIFE_TIME'))
TIMEOUT = int(os.getenv('TIMEOUT'))