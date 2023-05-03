import json
import logging
import pathlib

import telegram.ext
from telegram import Update
from telegram.ext import ContextTypes

import db as dbm
import service
from bot_handlers import common


def check_cb_data(data: str) -> bool:
    d = json.loads(data)
    return d.get('action', '') == 'simple_cmd'


class RunHandler:
    def __init__(self, db: dbm.Database, data_path: pathlib.Path):
        self.logger = logging.getLogger('run service')
        self.service = service.RunService(db, data_path)

    async def run(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.debug('run called')

        exc = await self.service.run(context.bot, update.effective_user, update.effective_message)
        if exc is not None:
            self.logger.warning(f'failed to execute run, {exc=}')
            await common.process_error(update, context)
            return

    async def repeat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.debug('repeat run called')

        cb_query = update.callback_query
        await cb_query.answer()

        data = json.loads(cb_query.data)

        exc = await self.service.run(context.bot, update.effective_user, telegram.Message(
            message_id=0,
            text=data['message'],
            date=...,
            chat=...,
        ))
        if exc is not None:
            self.logger.warning(f'failed to execute repeat run, {exc=}')
            await common.process_error(update, context)
            return

    def get_handlers(self) -> list[telegram.ext.BaseHandler]:
        return [
            telegram.ext.CommandHandler('run', self.run),
            telegram.ext.CallbackQueryHandler(self.repeat, check_cb_data),
        ]
