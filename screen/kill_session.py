import os

__all__ = ['kill_session']


def kill_session(session: str):
    os.system(f'screen -S {session} -X quit')
