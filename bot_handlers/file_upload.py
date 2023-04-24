import logging
import pathlib

import telegram
from telegram import Update
from telegram.ext import ContextTypes

import db as dbm
import service
from bot_handlers import common


class FileUploadHandler:
    def __init__(self, db: dbm.Database, root_path: pathlib.Path):
        self.logger = logging.getLogger('upload file handler')
        self.service = service.FileUploadService(db, root_path)

    async def file_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.debug('file upload called')

        exc = await self.service.upload_file(context.bot, update.effective_user, update.effective_message)
        if exc is not None:
            self.logger.warning(f'failed to execute file upload, {exc=}')
            await common.process_error(update, context)
            return

    def get_handler(self) -> telegram.ext.BaseHandler:
        return telegram.ext.MessageHandler(telegram.ext.filters.CaptionRegex(r'/upload'), self.file_upload)
