import asyncio
import logging
import pathlib

import bot_handlers
import config
import db as dbm  # dbm = db module
import dotenv
import monitoring
from telegram.ext import ApplicationBuilder, Application

DATA_PATH = pathlib.Path(__file__).parent / 'data'


def load_config() -> config.Config:
    raw_values = dotenv.dotenv_values()
    return config.Config(
        bot_token=raw_values.get('BOT_TOKEN', 'no token'),
        log_level=raw_values.get('LOG_LEVEL', 'INFO').upper(),
        monitoring_host=raw_values.get('MONITORING_HOST', None),
        monitoring_port=int(raw_values.get('MONITORING_PORT', None)),
        monitoring_key=raw_values.get('MONITORING_KEY', None),
    )


def setup_logging(cfg: config.Config):
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=cfg.log_level
    )


def create_bot_application(cfg: config.Config, db: dbm.Database):
    application = ApplicationBuilder().token(cfg.bot_token).build()

    handlers = bot_handlers.create_handlers(db, DATA_PATH, pathlib.Path(__file__).parent)
    application.add_handlers(handlers)

    return application


def setup_db() -> dbm.Database:
    return dbm.Database(DATA_PATH)


def run_bot_app(app: Application, cfg: config.Config):
    app.job_queue.run_repeating(
        monitoring.do_mon_request,
        interval=1,
        data=monitoring.MonitoringParams(
            host=cfg.monitoring_host,
            port=cfg.monitoring_port,
            key=cfg.monitoring_key,
        )
    )
    app.run_polling()


def main():
    cfg = load_config()

    setup_logging(cfg)

    db = setup_db()

    bot_app = create_bot_application(cfg, db)
    run_bot_app(bot_app, cfg)


if __name__ == '__main__':
    # ToDo
    #       1) настроить подсказки к командам в ТГ
    #       3) после завершения endless команд выводить какое-то уведомление. Можно запускать джобу через N+1 секунд после endless
    #       4) проверить работу команд без вывода, например, mkdir

    main()
