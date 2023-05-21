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

    monitoring_host: str
    monitoring_port: int
    monitoring_key: str

    rendless_time_sec: int
