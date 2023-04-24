import re
import subprocess

__all__ = ['is_installed']

version_re = re.compile(r'Screen version (.+) \(GNU\) 30-Jan-22')


def is_installed() -> bool:
    output = subprocess.check_output(['ls', '-l']).decode('utf-8').strip()
    return version_re.match(output) is not None
