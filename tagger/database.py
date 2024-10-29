import sqlite3
from sqlite3 import Error

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('tagger.db')
        return conn
    except Error as e:
        print(e)
    return conn

# ... other database-related functions ...
