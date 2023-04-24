__all__ = ['UserDB', 'UserModel']

import logging
import pathlib
import sqlite3
import typing
from dataclasses import dataclass

from . import db


@dataclass
class UserModel:
    tid: str
    name: str
    last_name: str
    logged_in: bool


@dataclass
class UserDB:
    db: db.Database
    logger: logging.Logger = logging.getLogger('user db')

    def check_status(self, tid: str) -> tuple[bool, typing.Optional[sqlite3.Error]]:
        self.logger.debug('check user status called')
        with open(pathlib.Path(__file__).parent / 'queries/check_user_status.sql') as fin:
            query = fin.read()

        try:
            cur = self.db.connection.execute(query, [tid])
            return cur.fetchone()[0], None
        except sqlite3.Error as error:
            self.logger.critical(f'Error getting user status: {error=}')
            return False, error

    def create_user_if_ne(self, tid: str, name: str):  # ne = not exists
        self.logger.debug('upsert user called')
        with open(pathlib.Path(__file__).parent / 'queries/upsert_user.sql') as fin:
            query = fin.read()

        try:
            with self.db.connection:
                cur = self.db.connection.execute(query, [tid, name, False])
                cur.close()
                self.logger.debug('upserted user successfully')
        except sqlite3.Error as error:
            self.logger.critical(f'Error upserting user: {error=}')
            return False, error

    def authorize_user(self, tid: str) -> typing.Optional[sqlite3.Error]:
        self.logger.debug('authorize user called')
        with open(pathlib.Path(__file__).parent / 'queries/set_user_logged_in.sql') as fin:
            query = fin.read()

        try:
            with self.db.connection:
                cur = self.db.connection.execute(query, [True, tid])
                cur.close()
                self.logger.debug('authorized user successfully')
        except sqlite3.Error as error:
            self.logger.critical(f'Error authorizing user: {error=}')
            return error

    def logout_user(self, tid: str) -> typing.Optional[sqlite3.Error]:
        self.logger.debug('logout user called')
        with open(pathlib.Path(__file__).parent / 'queries/set_user_logged_in.sql') as fin:
            query = fin.read()

        try:
            with self.db.connection:
                cur = self.db.connection.execute(query, [False, tid])
                cur.close()
                self.logger.debug('logout user successfully')
        except sqlite3.Error as error:
            self.logger.critical(f'Error logging out user: {error=}')
            return error
