import sys
import shlex
from typing import Union

def safe_posix(s: str) -> str:
    return shlex.quote(s)

def safe_win32(s: str) -> str:
    s = s.replace('"', '')
    return f'"{s}"' if s else ''

def safe(s: Union[str, None]) -> Union[str, None]:
    if s:
        if sys.platform == 'win32':
            s = safe_win32(s)
        else:
            s = safe_posix(s)
    return s if s else None
