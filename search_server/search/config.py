"""Search development configuration."""

import pathlib

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

# Secret key for encrypting cookies
SECRET_KEY = b'\x0e9\xbfu\xc1\xe6\xe2p7+k\xeerI\t\x1a\xcfs1 O\xb4m!'
SESSION_COOKIE_NAME = 'login'

# Index servers
SEARCH_INDEX_SEGMENT_API_URLS = [
    "http://localhost:9000/api/v1/hits/",
    "http://localhost:9001/api/v1/hits/",
    "http://localhost:9002/api/v1/hits/",
]

# File root
SEARCH_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

# Database file is var/search.sqlite3
DATABASE_FILENAME = SEARCH_ROOT/'var'/'search.sqlite3'
