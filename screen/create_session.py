import os
import random

__all__ = ['create_session']


def create_session() -> str:
    sess = 's' + str(random.randint(1_000_000, 1_000_000_000_000))
    os.system(f'screen -dmS {sess}')
    return sess
