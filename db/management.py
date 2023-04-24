_all__ = ['ManagementDB']
import logging
import pathlib
import sqlite3
from dataclasses import dataclass

from . import db as dbm

storage = dict()


@dataclass
class ManagementDB:
    db: dbm.Database
    logger: logging.Logger = logging.getLogger('management db')

    def get_string(self, key: str) -> tuple[str, bool]:
        self.logger.debug('management get string called')
        if key in storage:
            return storage[key]

        with open(pathlib.Path(__file__).parent / 'queries/get_management_by_key.sql') as fin:
            query = fin.read()

        try:
            cur = self.db.connection.execute(query, [key])
            res = cur.fetchone()
            if res is None:
                return '', False
            storage[key] = res[0]
            return res[0], True
        except sqlite3.Error as error:
            self.logger.critical(f'Error getting user status: {error=}')
            return '', False
