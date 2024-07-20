import asyncio
import sqlite3, sys
from queue import Queue
from threading import Thread

#ver 2.0

def get_loop(future: asyncio.Future) -> asyncio.AbstractEventLoop:
    if sys.version_info >= (3, 7):
        return future.get_loop()
    else:
        return future._loop

class DB_worker(Thread):
    def __init__(self, db_name):
        super().__init__()
        self.tasks = Queue()     
        self.db_name = db_name

    def run(self) -> None:
        self.adb = sqlite3.connect(self.db_name)

        def set_result(fut, result):
            if not fut.done():
                fut.set_result(result)

        while True:
            sql, params, commit_all, future, fetch, fetch_all = self.tasks.get()
            #print(sql)

            try:
                if sql != None:
                    if params == None:
                        cur = self.adb.execute(sql)

                    else:
                        cur = self.adb.execute(sql, params)

                    if future != None:
                        result = None

                        if fetch:
                            if fetch_all:
                                result = cur.fetchall()

                            else:
                                result = cur.fetchone()

                        get_loop(future).call_soon_threadsafe(set_result, future, result)

                if commit_all:
                    self.adb.commit()

            except Exception as ex:
                print('SQL exception:', ex)
                print(sql)

    def execute_nowait(self, sql, params=None, commit=True):
        task = (sql, params, commit, None, False, False)
        self.tasks.put_nowait(task)

    async def execute(self, sql, params=None, fetch=True, fetch_all=True, commit=False):
        future = asyncio.get_event_loop().create_future()

        task = (sql, params, commit, future, fetch, fetch_all)
        self.tasks.put_nowait(task)

        return await future

    def commit(self):
        task = (None, None, True, None, False, False)
        self.tasks.put_nowait(task)