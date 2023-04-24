import os

__all__ = ['run_in_session']

import time


def run_in_session(session: str, cmd: str):
    os.system(f'screen -r {session} -p0 -X stuff "{cmd}"')
    os.system(f'screen -r {session} -p0 -X eval "stuff \\015"')
    time.sleep(1)
