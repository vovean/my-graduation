import json
import logging
import pathlib

import telegram.ext
from telegram import Update
from telegram.ext import ContextTypes

import config
import db as dbm
import service
from bot_handlers import common
from service.inline_btn_data_keys import ACTION, MESSAGE_TEXT, REPLY_TO


class RendlessHandler:
    def __init__(self, db: dbm.Database, data_path: pathlib.Path, cfg: config.Config):
        self.logger = logging.getLogger('rendless handler')
        self.service = service.RendlessService(db, data_path, cfg)
        self.msgs_path = data_path / 'msgs'

    def check_cb_data(self, data: str) -> bool:
        with open(self.msgs_path / data, 'r') as fin:
            d = json.load(fin)

        return d.get(ACTION, '') == 'rendless_cmd'

    async def rendless(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.debug('rendless called')

        exc = await self.service.rendless(context.bot, update.effective_user, update.effective_message,
                                          context.job_queue)
        if exc is not None:
            self.logger.warning(f'failed to execute run, {exc=}')
            await common.process_error(update, context)
            return

    async def repeat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.debug('repeat run called')

        cb_query = update.callback_query
        await cb_query.answer()

        with open(self.msgs_path / cb_query.data) as fin:
            data = json.load(fin)

        exc = await self.service.rendless(context.bot, update.effective_user, telegram.Message(
            message_id=data.get(REPLY_TO, 0),
            text=data[MESSAGE_TEXT],
            date=...,
            chat=...,
        ), context.job_queue)
        if exc is not None:
            self.logger.warning(f'failed to execute repeat run, {exc=}')
            await common.process_error(update, context)
            return

    def get_handler(self) -> list[telegram.ext.BaseHandler]:
        return [
            telegram.ext.CommandHandler('rendless', self.rendless),
            telegram.ext.CallbackQueryHandler(self.repeat, self.check_cb_data),
        ]
