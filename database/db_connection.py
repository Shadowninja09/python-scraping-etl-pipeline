import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('HOST')
PASSWORD = os.getenv('PASSWORD')
USERNAME = os.getenv('DB_USERNAME')
PORT = os.getenv('PORT')
DATABASE = os.getenv('DATABASE')


def db_engine():
    connection_string = f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{DB_HOST}:{PORT}/{DATABASE}" 

    engine = create_engine(connection_string)
    return engine