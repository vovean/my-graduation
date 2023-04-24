import io
import logging
import os
import pathlib
import typing
import zipfile

import telegram

import db as dbm


def get_path(msg: str) -> str:
    s = msg.split(' ', maxsplit=1)
    return s[-1]


def zip_file(path: pathlib.Path) -> io.BytesIO:
    b = io.BytesIO()
    zf = zipfile.ZipFile(b, mode='w')
    zf.write(str(path.absolute()), path.name)
    zf.close()

    return b


def zip_dir(path: pathlib.Path) -> io.BytesIO:
    b = io.BytesIO()
    zf = zipfile.ZipFile(b, 'w', zipfile.ZIP_DEFLATED)

    rootlen = len(str(path.absolute())) + 1
    for base, dirs, files in os.walk(str(path.absolute())):
        for file in files:
            fn = os.path.join(base, file)
            zf.write(fn, fn[rootlen:])

    zf.close()
    b.seek(0)

    return b


class FileDownloadService:
    def __init__(self, db: dbm.Database):
        self.db = db
        self.logger = logging.getLogger('file download service')
        self.user_repo = dbm.UserDB(self.db)

    async def download_file(self,
                            bot: telegram.Bot,
                            user: telegram.User,
                            message: telegram.Message) -> typing.Optional[Exception]:
        self.logger.debug('download file called')

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

        path = pathlib.Path(get_path(message.text)).absolute()
        if not path.exists():
            self.logger.error(f'cannot create non-existent parent, parent={path.parent.absolute()}')
            await bot.send_message(
                chat_id=user.id,
                text=f'Файл или директория {path.parent.absolute()} не найдена. Обратитесь к администратору'
            )
            return None

        if path.is_dir():
            data = zip_dir(path)
            name = f'{path.name}.zip'
        else:
            data = str(path.absolute())
            name = path.name

        try:
            await bot.send_document(
                chat_id=tid,
                document=data,
                filename=name,
                caption=f'`{path.absolute()}`',
                parse_mode='Markdown',
            )
        except BaseException as exc:
            self.logger.error(f'failed to send file to user, {path=}, {exc=}')
            await bot.send_message(
                chat_id=user.id,
                text='Ошибка при отправке файла. Обратитесь к администратору'
            )
            return None
