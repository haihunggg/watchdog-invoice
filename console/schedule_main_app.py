import time
import os
import traceback
import subprocess
from datetime import datetime
import sys
import threading
from config import Config
import atexit


def delete_app_log():
    try:
        os.remove(os.path.join(Config.APP_LOG_FOLDER,'applog.txt'))
    except FileNotFoundError:
        pass
    except Exception:
        # traceback.print_exc()
        pass


def delete_app_log_loop():
    while True:
        day = 60*60*24
        day = 80
        time.sleep(day*3)
        delete_app_log()


_delete_app_log_thread = threading.Thread(
    daemon=True, target=delete_app_log_loop)
_delete_app_log_thread.start()


def save_check_point():
    with open("check_point.txt", mode='w') as file:
        s = datetime.now().isoformat()
        file.write(s)


def get_time_from_checkpoint() -> float:
    try:
        with open("check_point.txt", mode='r') as file:
            iso = file.read()
            dt = datetime.fromisoformat(iso)
            return dt.timestamp()
    except FileNotFoundError:
        return 0


def job():
    subprocess.run([sys.executable, "main_app.py"])


SEC_INTERVAL = 30


def sleep_on_first_run():

    last_run = get_time_from_checkpoint()  # 1000
    next_run = last_run + SEC_INTERVAL  # 1010

    curr_time = time.time()  # 10014

    sleep_time = next_run-curr_time
    if sleep_time >= 0:
        time.sleep(sleep_time)


def main():
    sleep_on_first_run()
    while True:
        try:
            job()
            save_check_point()
            time.sleep(SEC_INTERVAL)
        except KeyboardInterrupt:
            save_check_point()
            break


main()

def exit_handler():
    save_check_point()


atexit.register(exit_handler)

