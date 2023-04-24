import logging
import os
import pathlib
import typing

import telegram

import db as dbm


def get_path(msg: str) -> str:
    s = msg.split(' ', maxsplit=1)
    return s[-1]


class FileUploadService:
    def __init__(self, db: dbm.Database, root_path: pathlib.Path):
        self.db = db
        self.logger = logging.getLogger('file upload service')
        self.user_repo = dbm.UserDB(self.db)
        self.root_path = root_path

    async def upload_file(self,
                          bot: telegram.Bot,
                          user: telegram.User,
                          message: telegram.Message) -> typing.Optional[Exception]:
        self.logger.debug('upload file called')

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

        path = pathlib.Path(get_path(message.caption)).absolute()
        if not path.parent.exists():
            os.system(f'mkdir -p {path.parent.absolute()}')
        if not path.parent.exists():
            self.logger.error(f'cannot create non-existent parent, parent={path.parent.absolute()}')
            await bot.send_message(
                chat_id=user.id,
                text=f'Родительская директория {path.parent.absolute()} не найдена, создание невозможно. Обратитесь к администратору'
            )
            return None

        if self.root_path.absolute() in path.absolute().parents:
            self.logger.error(f'cannot upload files to this project directories, path={path.absolute()}')
            await bot.send_message(
                chat_id=user.id,
                text=f'Загрузка в {self.root_path.absolute()} и дочерние директорииc запрещена. Обратитесь к администратору'
            )
            return None

        try:
            file = await message.effective_attachment.get_file()
            if path.is_dir():
                path = path / message.effective_attachment.file_name
            downloaded = await file.download_to_drive(path)
        except telegram.error.TelegramError as exc:
            self.logger.error(f'failed to download the attachment, {exc=}')
            return exc

        await bot.send_message(
            chat_id=user.id,
            text=f'Файл успешно загружен по пути `{downloaded.absolute()}`',
            parse_mode='Markdown'
        )
