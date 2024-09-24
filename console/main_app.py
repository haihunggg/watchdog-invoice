import json
import sys
import psycopg2
import pandas as pd
import time
import os
from collections import defaultdict
from urllib.parse import quote_plus
from config import Config
from sqlalchemy import create_engine
from constants import *
from datetime import datetime as dt
import logging
from telegram_ import send_telegram_document
from utils import file_utils
import traceback

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

is_use_sql_error = '--error' in sys.argv
print(is_use_sql_error)

os.makedirs(Config.APP_LOG_FOLDER, exist_ok=True)

file_handler = logging.FileHandler(
    os.path.join(Config.APP_LOG_FOLDER, "applog.txt"))

file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s")
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


def format_file_name():
    now = str(dt.now())
    dot_index = now.rfind('.')
    return now[:dot_index].replace(' ', '_').replace('-', '').replace(':', '-')


def get_warnings():
    def get_info(host_slave, item: str) -> dict:
        res = {}

        for item in item.split(';')[:-1]:
            key, value = item.split('=')
            res[key] = value

        res["Host"] = host_slave
        return res

    try:
        result = []
        count = 0
        db_errors = []

        if is_use_sql_error:
            filename = 'query_error.sql'
        else:
            filename = 'query.sql'

        with open(f"resources/sql/{filename}") as sql_file:
            sending_tax = sql_file.read()

        try:
            with open("connectstring_config.json") as fo:
                ans = json.load(fo)

            for tenant_id, db in ans.items():
                querry_error_sending_tax = None
                database = db["Database"]
                user = db["User ID"]
                password = db["Password"]
                host = db["Host"]
                port = db["Port"]
                encoded_password = quote_plus(password)
                DATABASE_URI = f'postgresql://{user}:{encoded_password}@{host}:{port}/{database}'

                try:

                    engine = create_engine(DATABASE_URI)
                    with engine.connect() as conn:
                        querry_error_sending_tax = sending_tax.replace(
                            '?', tenant_id)
                        if is_use_sql_error:
                            checkpoint = file_utils.get_checkpoint()
                            querry_error_sending_tax = querry_error_sending_tax.replace(
                                "checkpoint", dt.fromtimestamp(checkpoint).isoformat())
                        df = pd.read_sql_query(querry_error_sending_tax, conn)
                        result.append(df)
                except Exception as e:
                    db_errors.append(DATABASE_URI)
                    count += 1

                time.sleep(3)
        except Exception as e:
            with open("resources/sql/connect.sql") as file:
                tenant_sql = file.read().strip()

            conn = psycopg2.connect(Config.DATABASE_URI)

            cur = conn.cursor()
            cur.execute(tenant_sql)
            ans = {}

            for tenantid, _, connectionstring in cur:
                if HOST_MASTER_1 in connectionstring:
                    ans[tenantid] = get_info(HOST_SLAVE_1, connectionstring)
                elif HOST_MASTER_2 in connectionstring:
                    ans[tenantid] = get_info(HOST_SLAVE_2, connectionstring)

            cur.close()
            conn.close()

            out = defaultdict(list)

            for tenant_id, conn_str in ans.items():
                out[tuple(conn_str.items())].append(tenant_id)

            with open("resources/sql/connect_cloud.sql") as sql_file:
                sending_tax_cloud = sql_file.read()

            for db_info, tenant_ids in out.items():
                db = dict(db_info)

                database = db["Database"].strip()
                user = db["User ID"]
                password = db["Password"]
                host = db["Host"]
                port = db["Port"]
                encoded_password = quote_plus(password)
                DATABASE_URI = f'postgresql://{user}:{encoded_password}@{host}:{port}/{database}'

                try:

                    engine = create_engine(DATABASE_URI)
                    with engine.connect() as conn:
                        for ten_id in tenant_ids:
                            querry_sending_tax = sending_tax.replace(
                                '?', ten_id)
                            checkpoint = file_utils.get_checkpoint()
                            querry_sending_tax = querry_sending_tax.replace(
                                "checkpoint", dt.fromtimestamp(checkpoint).isoformat())
                            df = pd.read_sql_query(querry_sending_tax, conn)
                            result.append(df)
                except Exception as e:
                    traceback.print_exc()
                    db_errors.append(f"{DATABASE_URI}: {e}")
                    count += 1

                time.sleep(3)

            try:
                engine = create_engine(Config.DATABASE_URI)

                with engine.connect() as conn:
                    tenant_ids_cloud = pd.read_sql_query(
                        sending_tax_cloud, conn)

                with engine.connect() as conn:
                    for ten_id in tenant_ids_cloud['Id'].astype(str):
                        querry_sending_tax = sending_tax.replace('?', ten_id)
                        df = pd.read_sql_query(querry_sending_tax, conn)
                        result.append(df)
            except Exception as e:
                traceback.print_exc()
                db_errors.append(f"{DATABASE_URI}: {e}")
                count += 1

        return result, db_errors, count

    except Exception as e:
        return "Không thể kết nối tới database: " + str(e)


try:
    logger.info("Starting the application")

    result, db_errors, count = get_warnings()

    errors = '\n'.join(db_errors)
    logger.info(f"error db number: {count}\n{errors}")

    ans = pd.concat(result, ignore_index=True)

    if len(ans) != 0:
        os.makedirs(Config.ERROR_INVOICE_FOLDER, exist_ok=True)
        file_name = f"{format_file_name()}.json"
        file_path = os.path.join(Config.ERROR_INVOICE_FOLDER, file_name)

        data = list(ans.to_dict(orient="index").values())
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        with open(file_path, "r", encoding="utf-8") as f:
            send_telegram_document('-4222451165', f, os.path.basename(file_path))

    logger.info("done")
    with open(os.path.join(Config.APP_LOG_FOLDER, 'done.txt'), mode='w') as f:
        f.write(dt.now().isoformat())

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)