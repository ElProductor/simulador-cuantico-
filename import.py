import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL", "postgres://usuario:contraseña@host:puerto/dbname")

def get_connection():
    return psycopg2.connect(DATABASE_URL)