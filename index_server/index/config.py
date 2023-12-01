"""Index Server development configuration."""

import os
import pathlib

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

# Secret key for encrypting cookies
SECRET_KEY = b'\x0e9\xbfu\xc1\xe6\xe2p7+k\xeerI\t\x1a\xcfs1 O\xb4m!'
SESSION_COOKIE_NAME = 'login'

# File locations
INDEX_SERVER_ROOT = pathlib.Path(__file__).resolve().parent
INVERTED_INDEX_FOLDER = INDEX_SERVER_ROOT/'inverted_index'
INDEX_PATH = os.getenv("INDEX_PATH", "inverted_index_1.txt")
STOPWORDS_FILE = INDEX_SERVER_ROOT/'stopwords.txt'
PAGERANK_FILE = INDEX_SERVER_ROOT/'pagerank.out'
STOPWORDS = []
PAGERANKS = {}
INVERTED_INDEX = {}
