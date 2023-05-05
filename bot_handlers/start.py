__all__ = ['StartHandler']

import logging

import telegram.ext
from telegram import Update
from telegram.ext import ContextTypes

import db as dbm
from . import common

GREETINGS_TEXT = '''
Привет!
Этот бот поможет управлять твоим сервером.

*Список команд:*
1. /start - показать это сообщение
2. /login - войти в режим управления серверов
3. /logout - выйти из режима управления сервером
4. /run - запустить команду с *конечным* выводом (например, `ls`)
5. /rendless - запустить команду с *бесконечным* выводом (например, `top`)
6. /upload - загрузить файл по указанному пути
7. /download - скачать файл, находящийся по указанному пути
8. /help - вывести подробную справку по команде

Статус пользователя: {user_status}
'''.strip()


def create_user_status_text(user_logged_in: bool) -> str:
    if user_logged_in:
        return 'Авторизован'
    return 'Не авторизован. Для авторизации используйте /login'


def fill_greetings_text(user_logged_in: bool) -> str:
    return GREETINGS_TEXT.format(
        user_status=create_user_status_text(user_logged_in),
    )


class StartHandler:
    def __init__(self, db: dbm.Database):
        self.db = db
        self.logger = logging.getLogger('start logger')
        self.user_repo = dbm.UserDB(self.db)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.debug('start called')

        tid = str(update.effective_user.id)
        self.user_repo.create_user_if_ne(tid, update.effective_user.full_name)

        is_user_logged_in, exc = self.user_repo.check_status(tid)
        if exc is not None:
            self.logger.error(f'error checking user is_logged_in {exc=}')
            await common.process_error(update, context)
            return

        text = fill_greetings_text(is_user_logged_in)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode='Markdown'
        )

    def get_handler(self) -> telegram.ext.BaseHandler:
        return telegram.ext.CommandHandler('start', self.start)
