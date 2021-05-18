import pickle
from pathlib import Path
from datetime import date, datetime

ky_file = Path(__file__).parent / 'ky_file~'

def get_ky_date() -> date:
    with open(ky_file, 'rb') as f:
        return pickle.load(f)

def set_ky_date(month: int, day: int):
    ky_date = date(datetime.now().year, month, day)
    if ky_date <= datetime.now().date():
        ky_date.year += 1
    with open(ky_file, 'wb') as f:
        pickle.dump(ky_date, f)

if not ky_file.exists():
    set_ky_date(12, 22)
