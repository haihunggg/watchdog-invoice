from urllib.parse import quote_plus


class Config:
    user = "minvoice"
    password = "Minvoice@123"
    encoded_password = quote_plus(password)
    DATABASE_URI = f'postgresql://{user}:{encoded_password}@103.61.122.194:5432/MinvoiceCloud'
    ERROR_INVOICE_FOLDER = "error_invoice"
    APP_LOG_FOLDER = "applog"
    LOOP_JOB_INTERVAL = 30
    JOB_TIMEOUT = 2*60*60
    JOB_TIMEOUT = 20
