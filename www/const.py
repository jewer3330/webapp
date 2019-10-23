import re
_COOKIE_KEY = '123'
_COOKIE_NAME = 'abc'
_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')
_EMAIL_TEMPLATE = ''
_EMAIL_SERVER = 'http://127.0.0.1:8000'
_TIME_WEEK_SECONDS = 60 * 60 * 24 * 7
