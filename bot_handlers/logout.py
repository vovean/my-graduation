import logging

import telegram.ext
from telegram import Update
from telegram.ext import ContextTypes

import db as dbm


class LogoutHandler:
    def __init__(self, db: dbm.Database):
        self.db = db
        self.logger = logging.getLogger('logout handler')
        self.user_repo = dbm.UserDB(self.db)

    async def logout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.debug('logout called')

        tid = str(update.effective_user.id)
        self.user_repo.create_user_if_ne(tid, update.effective_user.full_name)

        exc = self.user_repo.logout_user(tid)
        if exc is not None:
            self.logger.error(f'error logouting user, {exc=}')
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text='Ошибка на стороне сервера. Обратитесь к администратору',
            )
            return

        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text='Режим управления сервером отключен',
        )

    def get_handler(self) -> telegram.ext.BaseHandler:
        return telegram.ext.CommandHandler('logout', self.logout)
