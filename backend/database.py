import os
import psycopg2
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)


def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="infratrace",
        user="postgres",
        password=os.getenv("DB_PASSWORD"),
        port="5432"
    )