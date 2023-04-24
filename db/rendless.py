import logging
import pathlib
import sqlite3
import typing
from dataclasses import dataclass

from . import db


@dataclass
class RendlessModel:
    id: str
    user_tid: str
    is_active: bool
    command: str
    screen_session: str
    hardcopy: pathlib.Path


@dataclass
class RendlessDB:
    db: db.Database
    logger: logging.Logger = logging.getLogger('rendless db')

    def create_command(self, rm: RendlessModel) -> typing.Optional[sqlite3.Error]:
        self.logger.debug('create rendless command called')
        with open(pathlib.Path(__file__).parent / 'queries/create_rendless.sql') as fin:
            query = fin.read()

        try:
            with self.db.connection:
                cur = self.db.connection.execute(
                    query,
                    [rm.id, rm.user_tid, rm.is_active, rm.command, rm.screen_session, str(rm.hardcopy.absolute())],
                )
                cur.close()
        except sqlite3.Error as error:
            self.logger.critical(f'Error getting user status: {error=}')
            return error

    def stop_all_active(self) -> tuple[list[str], typing.Optional[sqlite3.Error]]:
        self.logger.debug('stop_all_active called')
        with open(pathlib.Path(__file__).parent / 'queries/stop_active_rendless.sql') as fin:
            query = fin.read()

        try:
            with self.db.connection:
                cur = self.db.connection.execute(query)
                res = cur.fetchall()
                res = [r[0] for r in res]
                return res, None
        except sqlite3.Error as error:
            self.logger.critical(f'Error setting active rendless commands inactive: {error=}')
            return [], error

    def stop_all_active_for_tid(self, tid: str) -> tuple[list[str], typing.Optional[sqlite3.Error]]:
        self.logger.debug('stop_all_active called')
        with open(pathlib.Path(__file__).parent / 'queries/stop_active_rendless_for_tid.sql') as fin:
            query = fin.read()

        try:
            with self.db.connection:
                cur = self.db.connection.execute(query, [tid])
                res = cur.fetchall()
                res = [r[0] for r in res]
                return res, None
        except sqlite3.Error as error:
            self.logger.critical(f'Error setting active rendless commands inactive: {error=}')
            return [], error
