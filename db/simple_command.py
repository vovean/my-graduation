import logging
import pathlib
import sqlite3
import typing
from dataclasses import dataclass

from . import db


@dataclass
class SimpleCommandModel:
    id: str
    command: str
    output_file: str
    text_response_mid: str


@dataclass
class SimpleCommandDB:
    db: db.Database
    logger: logging.Logger = logging.getLogger('simple command db')

    def save_command(self, sm: SimpleCommandModel) -> typing.Optional[sqlite3.Error]:
        self.logger.debug('save simple command called')
        with open(pathlib.Path(__file__).parent / 'queries/save_simple_command.sql') as fin:
            query = fin.read()

        try:
            with self.db.connection:
                cur = self.db.connection.execute(
                    query,
                    [sm.id, sm.command, sm.output_file, sm.text_response_mid],
                )
                cur.close()
        except sqlite3.Error as error:
            self.logger.critical(f'Error getting user status: {error=}')
            return error
