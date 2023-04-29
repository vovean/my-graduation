import json
import logging
import os
import pathlib
import typing
import uuid
from datetime import datetime

import telegram

import db as dbm


def extract_command_from_msg(msg: str) -> str:
    return msg.split(' ', maxsplit=1)[-1]


def make_inline_buttons(msg: str) -> telegram.InlineKeyboardMarkup:
    buttons = [[telegram.InlineKeyboardButton(
        'Повторить',
        callback_data=json.dumps({
            'action': 'simple_cmd',
            'message': msg,
        })
    )]]

    return telegram.InlineKeyboardMarkup(buttons)


class RunService:
    def __init__(self, db: dbm.Database, data_path: pathlib.Path):
        self.db = db
        self.logger = logging.getLogger('run service')
        self.user_repo = dbm.UserDB(self.db)
        self.simple_cmd_repo = dbm.SimpleCommandDB(self.db)
        self.outputs_path = data_path / 'output'

    async def run(self,
                  bot: telegram.Bot,
                  user: telegram.User,
                  message: telegram.Message) -> typing.Optional[Exception]:
        self.logger.debug('run called')

        tid = str(user.id)
        self.user_repo.create_user_if_ne(tid, user.full_name)

        is_user_logged_in, exc = self.user_repo.check_status(tid)
        if exc is not None:
            self.logger.error(f'error checking user is_logged_in {exc=}')
            return exc
        if not is_user_logged_in:
            self.logger.error(f'user not logged in, {tid=}')
            await bot.send_message(
                chat_id=user.id,
                text='Режим управления сервером не активен. Для активации воспользуйтесь командой /login'
            )
            return None

        command = extract_command_from_msg(message.text)
        output_file = (self.outputs_path / f'{int(datetime.now().timestamp())}.txt').absolute()
        self.logger.debug(f'running {command=}')
        os.system(f'{command} > {output_file}')

        with open(output_file) as fin:
            result = fin.read()

        reply_markup = make_inline_buttons(message.text)
        if result.count('\n') <= 20:
            msg = await bot.send_message(
                chat_id=user.id,
                text=f'```\n{result}\n```',
                parse_mode='Markdown',
                reply_markup=reply_markup,
            )
        else:
            msg = await bot.send_document(
                chat_id=user.id,
                caption='Вывод команды очень большой. Для удобства прислал файлом',
                document=output_file,
                filename='command_output.txt',
                reply_markup=reply_markup,
            )

        sm = dbm.SimpleCommandModel(
            id=str(uuid.uuid4()),
            command=command,
            output_file=str(output_file),
            text_response_mid=str(msg.id),
            image_response_mid='',
        )
        exc = self.simple_cmd_repo.save_command(sm)
        if exc is not None:
            await bot.send_message(
                chat_id=user.id,
                text=f'Произошла серверная ошибка. Обратитесь к администратору',
                parse_mode='Markdown',
            )
