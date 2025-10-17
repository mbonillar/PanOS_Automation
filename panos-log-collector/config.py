import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    load_dotenv()
    SECRET_KEY =  os.getenv('secret_key')
    MAIL_SERVER = ''
    MAIL_PORT = 25
    FLASK_DEBUG = 1