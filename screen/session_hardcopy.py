import os
import pathlib

__all__ = ['session_hardcopy']


def session_hardcopy(session: str, path: pathlib.Path):
    os.system(f'screen -U -r {session} -p0 -X hardcopy {path.absolute()}')
