__all__ = ['Database']

import logging
import pathlib
import sqlite3
import typing
import uuid


def setup_connection(root_path: pathlib.Path, logger: logging.Logger) -> typing.Tuple[sqlite3.Connection, bool]:
    db_path = root_path / 'db.sqlite3'
    exists = db_path.exists()

    try:
        sqlite_connection = sqlite3.connect(db_path)
        cursor = sqlite_connection.cursor()
        logger.debug(f'DB connection created: {db_path=}')

        cursor.execute('select sqlite_version();')
        record = cursor.fetchall()
        logging.debug(f'SQLite version: {record}')
        cursor.close()

        return sqlite_connection, not exists

    except sqlite3.Error as error:
        logger.critical(f'Error connecting to DB: {db_path=}, {error=}')
        exit(1)


class Database:
    connection: sqlite3.Connection
    logger: logging.Logger

    def __init__(self, data_path: pathlib.Path):
        self.logger = logging.getLogger('database')
        self.connection, new_db = setup_connection(data_path, self.logger)

        if new_db:
            self.setup_schema()
            self.create_secret_key()

    def setup_schema(self):
        self.logger.debug('setup schema called')
        with open(pathlib.Path(__file__).parent / 'queries/setup_schema.sql') as fin:
            script = fin.read()

        try:
            with self.connection:
                cur = self.connection.executescript(script)
                cur.close()
        except sqlite3.Error as error:
            self.logger.critical(f'Error creating schema: {error=}')
            exit(1)

    def create_secret_key(self):
        self.logger.debug('create secret key called')
        with open(pathlib.Path(__file__).parent / 'queries/create_secret_key.sql') as fin:
            query = fin.read()

        try:
            with self.connection:
                cur = self.connection.execute(query, [str(uuid.uuid4())])
                secret_key = cur.fetchone()[0]
                cur.close()

            self.logger.critical(f'Секретный ключ: {secret_key}\n'
                                 f'Данный ключ необходимо предоставить боту в команде /login для получения доступа к управлению сервером.\n'
                                 f'Сохраните его, так как больше программа его никогда не покажет')

        except sqlite3.Error as error:
            self.logger.critical(f'Error creating secret key: {error=}')
            exit(1)
