from datetime import datetime


def get_checkpoint() -> float:
    try:
        with open("check_point.txt", mode='r') as file:
            iso = file.read()
            dt = datetime.fromisoformat(iso)
            return dt.timestamp()
    except FileNotFoundError:
        return datetime.now().timestamp()
