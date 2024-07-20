from utils.db import DB_worker
import os
from enum import Enum
import sqlite3

if not os.path.exists('files'):
    os.mkdir('files')


database = DB_worker('files/bot_db.sqlite')
database.start()

database.execute_nowait("""CREATE TABLE IF NOT EXISTS games (
        game INTEGER PRIMARY KEY AUTOINCREMENT,
        login BIGINT,
        moves INTEGER,
        distance FLOAT,
        winner BOOL
    )""")


database.execute_nowait("""CREATE TABLE IF NOT EXISTS meaning (
        game INTEGER,
        login BIGINT,
        meaning_1 INTEGER,
        meaning_2 INTEGER,
        move INTEGER
    )""")
                        


database.execute_nowait("""CREATE TABLE IF NOT EXISTS users (
        login BIGINT UNIQUE
    )""")
