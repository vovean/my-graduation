import hashlib
import json
import logging
import pathlib
import typing
import uuid
from dataclasses import dataclass

import telegram.ext

import db as dbm
import screen


def extract_command_from_msg(msg: str) -> str:
    return msg.split(' ', maxsplit=1)[-1]


def make_inline_buttons(msg: str) -> telegram.InlineKeyboardMarkup:
    buttons = [[telegram.InlineKeyboardButton(
        'Повторить',
        callback_data=json.dumps({
            'action': 'rendless_cmd',
            'message': msg,
        })
    )]]

    return telegram.InlineKeyboardMarkup(buttons)


@dataclass
class JobArgs:
    rm: dbm.RendlessModel
    user_tid: int | str
    mid: int
    inline_reply_markup: telegram.InlineKeyboardMarkup
    prev_msg_hash: str = ''


class RendlessService:
    def __init__(self, db: dbm.Database, data_path: pathlib.Path):
        self.db = db
        self.logger = logging.getLogger('rendless service')
        self.user_repo = dbm.UserDB(self.db)
        self.rendless_repo = dbm.RendlessDB(self.db)
        self.hardcopies_path = data_path / 'hardcopies'

        self.clear_existing_active_rendlesses()

    def clear_existing_active_rendlesses(self):
        sessions, exc = self.rendless_repo.stop_all_active()
        if exc is not None:
            self.logger.critical(f'failed to init rendless repo, {exc=}')
            exit(1)

        for sess in sessions:
            screen.kill_session(sess)

    def stop_all_rendless_for_tid(self, tid: str, jq: telegram.ext.JobQueue) -> Exception:
        sessions, exc = self.rendless_repo.stop_all_active_for_tid(tid)
        if exc is not None:
            self.logger.error(f'error checking user is_logged_in {exc=}')
            return exc

        for sess in sessions:
            screen.kill_session(sess)
            for job in jq.get_jobs_by_name(sess):
                self.logger.debug(f'stopping job {job.name}')
                job.schedule_removal()

    async def rendless(self,
                       bot: telegram.Bot,
                       user: telegram.User,
                       message: telegram.Message,
                       job_queue: telegram.ext.JobQueue) -> typing.Optional[Exception]:
        self.logger.debug('rendless called')

        tid = str(user.id)
        self.user_repo.create_user_if_ne(tid, user.full_name)

        exc = self.stop_all_rendless_for_tid(tid, job_queue)
        if exc is not None:
            return exc

        command = message.text.split(maxsplit=1)[-1]
        session = screen.create_session()
        hcopy_path = self.hardcopies_path / f'{session}.txt'
        rm = dbm.RendlessModel(
            id=str(uuid.uuid4()),
            user_tid=tid,
            is_active=True,
            command=command,
            screen_session=session,
            hardcopy=hcopy_path
        )

        is_user_logged_in, exc = self.user_repo.check_status(str(tid))
        if exc is not None:
            self.logger.error(f'error checking user is_logged_in {exc=}')
            return exc
        if not is_user_logged_in:
            self.logger.error(f'user not logged in, {tid=}')
            await bot.send_message(
                chat_id=tid,
                text='Режим управления сервером не активен. Для активации воспользуйтесь командой /login'
            )
            return None

        exc = self.rendless_repo.create_command(rm)
        if exc is not None:
            await bot.send_message(
                chat_id=tid,
                text='Ошибка при запуске команды. Обратитесь к администратору.'
            )
            return None

        screen.run_in_session(rm.screen_session, rm.command)

        # самое первое сообщение, которое потом будет лишь редактироваться
        screen.session_hardcopy(rm.screen_session, rm.hardcopy)
        with open(rm.hardcopy) as fin:
            data = fin.read()
        reply_markup = make_inline_buttons(message.text)
        message = await bot.send_message(
            chat_id=tid,
            text=f'```\n{data}\n```',
            parse_mode='Markdown',
            reply_markup=reply_markup,
        )

        job_queue.run_repeating(
            self.job,
            interval=1,
            last=10,
            user_id=user.id,
            name=session,
            data=JobArgs(
                rm=rm,
                user_tid=tid,
                mid=message.id,
                inline_reply_markup=reply_markup,
            )
        )

    async def job(self, context: telegram.ext.CallbackContext):
        jobargs: JobArgs = context.job.data
        screen.session_hardcopy(jobargs.rm.screen_session, jobargs.rm.hardcopy)
        with open(jobargs.rm.hardcopy) as fin:
            data = fin.read()

        hash = hashlib.md5(data.encode('utf-8')).hexdigest()
        if hash == jobargs.prev_msg_hash:
            self.logger.debug('message was not modified on this job run')
            return

        try:
            await context.bot.edit_message_text(
                chat_id=jobargs.user_tid,
                message_id=jobargs.mid,
                text=f'```\n{data}\n```',
                parse_mode='Markdown',
                reply_markup=jobargs.inline_reply_markup,
            )
            jobargs.prev_msg_hash = hash
        except telegram.error.BadRequest as exc:
            self.logger.warning(f'error occurred while editing message {jobargs.mid=}, {exc=}')
