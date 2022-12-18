from os import environ

BOT_TOKEN = environ['BOT_TOKEN']
ADMINS = environ['ADMINS'][1:-1].split(',')
DATABASE_URL = environ['DATABASE_URL']+'?sslmode=require'
LINUX = bool(environ['LINUX'])
LOG_CHAT = int(environ['LOG_CHAT'])