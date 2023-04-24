from dataclasses import dataclass


@dataclass
class Config:
    bot_token: str

    '''
    Допустимые уровни:
        CRITICAL
        FATAL
        ERROR
        WARN
        WARNING
        INFO
        DEBUG
        NOTSET
    '''
    log_level: str
