import traceback
import os
from collections import Counter
from datetime import datetime

import json
import psycopg2
from flask import jsonify, Flask, request
from config import Config
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
from constants import *

app = Flask(__name__)

# Replace with a strong secret
app.config["JWT_SECRET_KEY"] = Config.SECRET_KEY
jwt = JWTManager(app)

app.config.from_object(Config)


@jwt.invalid_token_loader
def custom_message(*args, **kwargs):
    return jsonify({
        "msg": "Token không đúng. Vui lòng kiểm tra lại"
    })


@app.route("/api/token")
def get_token():
    access_token = create_access_token(identity=app.config["JWT_SECRET_KEY"])
    return jsonify(access_token=access_token)


@app.route("/api/count")
@jwt_required()
def count_sendinginvoices():
    try:
        # start, end
        start_date = request.args.get('start')
        end_date = request.args.get('end')

        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

        error_files = os.listdir(Config.ERROR_INVOICE_FOLDER)

        ans = []

        for json_file in error_files:
            json_path = os.path.join(Config.ERROR_INVOICE_FOLDER, json_file)
            date_string = json_file.split('_')[0]
            date_format = "%Y%m%d"
            date_obj = datetime.strptime(date_string, date_format).date()

            if start_date_obj <= date_obj <= end_date_obj:
                with open(json_path, encoding="utf8") as jf:
                    res = json.load(jf)
                    ans.extend(res)

        count_taxcodes = len(set(x["TaxCode"] for x in ans))

        companies = [
            f'{company_info["TaxCode"]} - {company_info["SellerLegalName"]}'
            for company_info in ans
        ]

        result = dict(Counter(companies))

        return jsonify({"so_luong_mst": count_taxcodes, "chi_tiet": result})
    except KeyError:
        return jsonify(msg="Missing identity in token"), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify(msg=str(e))


@app.route("/api/warnings", methods=["GET"])
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

        conn = psycopg2.connect(app.config['DATABASE_URI'])

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

        return jsonify(ans)

    except Exception as e:
        return jsonify({"Không thể kết nối tới database": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
