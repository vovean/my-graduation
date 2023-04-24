import logging

import telegram
from telegram import Update
from telegram.ext import ContextTypes

import db as dbm
import service
from bot_handlers import common


class FileDownloadHandler:
    def __init__(self, db: dbm.Database):
        self.logger = logging.getLogger('download file handler')
        self.service = service.FileDownloadService(db)

    async def file_download(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.debug('file download called')

        exc = await self.service.download_file(context.bot, update.effective_user, update.effective_message)
        if exc is not None:
            self.logger.warning(f'failed to execute file download, {exc=}')
            await common.process_error(update, context)
            return

    def get_handler(self) -> telegram.ext.BaseHandler:
        return telegram.ext.CommandHandler('download', self.file_download)
