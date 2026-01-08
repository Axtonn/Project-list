import sqlite3
from pathlib import Path


class DbWriter:
    DB_PATH = str(Path(__file__).parent.parent.parent) + "/data/oic_careers.db"

    def __init__(self) -> None:
        self.con = sqlite3.connect(self.DB_PATH)
        self.con.execute("PRAGMA foreign_keys = 1")
        self.cur = self.con.cursor()

    def execute(self, sql: str, params: tuple = ()) -> None:
        '''
        Wrapper for `cur.execute(sql_query)` ensuring transactions are completed
        upon success or rolled back upon failure.
        '''
        try:
            with self.con:
                return self.cur.execute(sql, params)
        except sqlite3.Error:
            return None

    def end_session(self):
        self.con.close()
