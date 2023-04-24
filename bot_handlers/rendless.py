import logging
import pathlib

import telegram.ext
from telegram import Update
from telegram.ext import ContextTypes

import db as dbm
import service
from bot_handlers import common


class RendlessHandler:
    def __init__(self, db: dbm.Database, data_path: pathlib.Path):
        self.logger = logging.getLogger('rendless handler')
        self.service = service.RendlessService(db, data_path)

    async def rendless(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.debug('rendless called')

        exc = await self.service.rendless(context.bot, update.effective_user, update.effective_message, context.job_queue)
        if exc is not None:
            self.logger.warning(f'failed to execute run, {exc=}')
            await common.process_error(update, context)
            return

    def get_handler(self) -> telegram.ext.BaseHandler:
        return telegram.ext.CommandHandler('rendless', self.rendless)
