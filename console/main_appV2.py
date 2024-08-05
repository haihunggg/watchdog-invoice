import json

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
from telegram_ import send_telegram_message

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

os.makedirs(Config.APP_LOG_FOLDER, exist_ok=True)

file_handler = logging.FileHandler(os.path.join(Config.APP_LOG_FOLDER, "applog.txt"))

file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s")
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
        with open("resources/sql/connect.sql") as file:
            tenant_sql = file.read().strip()

        conn = psycopg2.connect(Config.DATABASE_URI)

        cur = conn.cursor()
        cur.execute(tenant_sql)

        ans = {}

        for tenantid, name, connectionstring in cur:
            if HOST_MASTER_1 in connectionstring:
                ans[tenantid] = get_info(HOST_SLAVE_1, connectionstring)
            elif HOST_MASTER_2 in connectionstring:
                ans[tenantid] = get_info(HOST_SLAVE_2, connectionstring)

        cur.close()
        conn.close()

        return ans

    except Exception as e:
        return "Không thể kết nối tới database: " + str(e)
    
try:
    logger.info("Starting the application")
    # resp = requests.get("http://host.docker.internal/api/warnings").json()
    resp = get_warnings()
    # resp = {'3a066711-48cb-71cf-17c8-5288f370c008': {'Database': 'MinvoiceCloud', 'Host': '103.61.122.194', 'Password': 'Minvoice@123', 'Port': '5432', 'User ID': 'minvoice'}}
    out = defaultdict(list)

    for tenant_id, conn_str in resp.items():
        out[tuple(conn_str.items())].append(tenant_id)

    with open("resources/sql/querry.sql") as sql_file:
        sending_tax = sql_file.read()

    with open("resources/sql/connect_cloud.sql") as sql_file:
        sending_tax_cloud = sql_file.read()

    result = []
    count = 0
    db_errors = []

    for db_info, tenant_ids in out.items():
        db = dict(db_info)

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
                for ten_id in tenant_ids:
                    querry_sending_tax = sending_tax.replace('?', ten_id)
                    df = pd.read_sql_query(querry_sending_tax, conn)
                    result.append(df)
        except Exception as e:
            db_errors.append(DATABASE_URI)
            count += 1

        time.sleep(3)

    try:
        engine = create_engine(Config.DATABASE_URI)

        with engine.connect() as conn:
            tenant_ids_cloud = pd.read_sql_query(sending_tax_cloud, conn)


        with engine.connect() as conn:
            for ten_id in tenant_ids_cloud['Id'].astype(str):
                querry_sending_tax = sending_tax.replace('?', ten_id)
                df = pd.read_sql_query(querry_sending_tax, conn)
                result.append(df)
    except Exception as e:
        print(e)
        db_errors.append(Config.DATABASE_URI)
        count += 1

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

        send_telegram_message('6720464969', file_path)

    # if len(df) == 0:
    #     engine = create_engine(Config.DATABASE_URI)
    #     df = pd.read_sql_query(sending_tax, con=engine)
    #     print(df)
    logger.info("done")

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)
