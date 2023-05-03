import pathlib

from telegram.ext import BaseHandler

import db as dbm
from .file_download import FileDownloadHandler
from .file_upload import FileUploadHandler
from .login import LoginHandler
from .logout import LogoutHandler
from .rendless import RendlessHandler
from .run import RunHandler
from .start import StartHandler


def create_handlers(db: dbm.Database, data_path: pathlib.Path, root_path: pathlib.Path) -> list[BaseHandler]:
    handlers = [
        StartHandler(db).get_handler(),
        LoginHandler(db).get_handler(),
        LogoutHandler(db).get_handler(),
        *RunHandler(db, data_path).get_handlers(),
        *RendlessHandler(db, data_path).get_handler(),
        FileUploadHandler(db, root_path).get_handler(),
        FileDownloadHandler(db).get_handler(),
    ]

    return handlers
