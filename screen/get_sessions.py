import subprocess

__all__ = ['get_sessions']


def get_sessions() -> list[str]:
    output = subprocess.check_output(['screen', '-ls']).decode('utf-8').strip()
    if output.startswith('No Sockets found'):
        return []
    if output.startswith('There are screens on') or output.startswith('There is a screen on'):
        lines = output.splitlines()
        sess_lines = lines[1:-1]
        sessions = []
        for line in sess_lines:
            sess = line.strip().split()[0]
            sessions.append(sess)
        return sessions
    return []
