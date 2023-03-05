from os import getenv
from dotenv import load_dotenv


load_dotenv()
BOT_TOKEN = getenv('BOT_TOKEN')
ADMINS = [int(admin.strip()) for admin in getenv('ADMINS').split(',')]
DB_HOST = getenv('DB_HOST')
DB_NAME = getenv('DB_NAME')
DB_USER = getenv('DB_USER')
DB_PASS = getenv('DB_PASS')
LINUX = getenv('LINUX')
LOG_CHAT = getenv('LOG_CHAT')
ADMIN_LOG_CHAT = getenv('ADMIN_LOG_CHAT')
