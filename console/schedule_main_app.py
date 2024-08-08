import time
import os
import traceback
import subprocess
from datetime import datetime
import sys
import threading
from config import Config
from utils import file_utils


class JobTimeoutError(Exception):
    pass


def delete_app_log():
    try:
        os.remove(os.path.join(Config.APP_LOG_FOLDER, 'applog.txt'))
    except FileNotFoundError:
        pass
    except Exception:
        # traceback.print_exc()
        pass


def delete_app_log_loop():
    while True:
        day = 60*60*24
        time.sleep(day*3)
        delete_app_log()


_delete_app_log_thread = threading.Thread(
    daemon=True, target=delete_app_log_loop)
_delete_app_log_thread.start()


CHECK_CRASH_FILE_NAME = "check-crash.txt"
LAST_RUN_FILE_NAME = "lastrun.txt"
param_sql_file = "query_error.sql"


def write_error_file(is_crashed: bool, file_name):
    with open(os.path.join(Config.APP_LOG_FOLDER, file_name), mode='w') as err_file:
        err_file.write(str(is_crashed))


def read_error_file(file_name):
    try:
        with open(os.path.join(Config.APP_LOG_FOLDER, file_name)) as err_file:
            return bool(eval((err_file.read())))
    except FileNotFoundError:
        return False


def save_check_point(dt: datetime | None = None):
    with open("check_point.txt", mode='w') as file:
        if dt is None:
            dt = datetime.now()

        s = dt.isoformat()
        file.write(s)


def get_last_done() -> datetime:
    try:
        with open(os.path.join(Config.APP_LOG_FOLDER, 'done.txt')) as f:
            s = f.read()
            return datetime.fromisoformat(s)
    except FileNotFoundError:
        return datetime.now()


def job():
    last_run_bool = read_error_file(file_name=LAST_RUN_FILE_NAME)
    check_crash_bool = read_error_file(file_name=CHECK_CRASH_FILE_NAME)

    cp_time = datetime.fromtimestamp(file_utils.get_checkpoint())
    now = datetime.now()
    interval = now - cp_time

    if last_run_bool or check_crash_bool or interval.seconds > Config.JOB_TIMEOUT:
        subprocess.check_output(
            [sys.executable, "main_app.py", '--error'])

        if last_run_bool:
            write_error_file(False, file_name=LAST_RUN_FILE_NAME)

        if check_crash_bool:
            write_error_file(False, file_name=CHECK_CRASH_FILE_NAME)

    else:
        subprocess.check_output(
            [sys.executable, "main_app.py"])


def main():
    while True:
        try:
            job()
            save_check_point()
            time.sleep(Config.LOOP_JOB_INTERVAL)
        except KeyboardInterrupt:
            save_check_point()
            write_error_file(True, file_name=CHECK_CRASH_FILE_NAME)
            break
        except Exception:
            save_check_point()
            write_error_file(True, file_name=CHECK_CRASH_FILE_NAME)

            traceback.print_exc()


main()
