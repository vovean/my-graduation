import logging
import re

import telegram.ext
from telegram import Update
from telegram.ext import ContextTypes

import db as dbm

correct_msg = re.compile(r'/login\s[\w-]+')
management_secret_key = 'secret_key'


def extract_key_from_msg(msg: str) -> str:
    if correct_msg.match(msg) is None:
        return ''
    return msg.split(' ', maxsplit=1)[-1]


class LoginHandler:
    def __init__(self, db: dbm.Database):
        self.db = db
        self.logger = logging.getLogger('login handler')
        self.user_repo = dbm.UserDB(self.db)
        self.management_repo = dbm.ManagementDB(self.db)

    async def login(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.debug('login called')

        tid = str(update.effective_user.id)
        self.user_repo.create_user_if_ne(tid, update.effective_user.full_name)

        key = extract_key_from_msg(update.effective_message.text.strip())
        if key == '':
            self.logger.debug('user message didnt match regexp')
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text='Авторизация не разрешена. Попробуйте еще раз',
            )
            return

        correct_key, found = self.management_repo.get_string(management_secret_key)
        if not found:
            self.logger.error(f'secret key not found')
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text='Ошибка на стороне сервера. Обратитесь к администратору',
            )
            return

        if key != correct_key:
            self.logger.debug('user provided an incorrect key')
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text='Авторизация не разрешена. Попробуйте еще раз',
            )
            return

        exc = self.user_repo.authorize_user(tid)
        if exc is not None:
            self.logger.error(f'error authorizing user, {exc=}')
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text='Ошибка на стороне сервера. Обратитесь к администратору',
            )
            return

        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text='Авторизация успешна',
        )

    def get_handler(self) -> telegram.ext.BaseHandler:
        return telegram.ext.CommandHandler('login', self.login)
