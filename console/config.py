from urllib.parse import quote_plus


class Config:
    user = "postgres"
    password = "Jarvis@123!@#"
    encoded_password = quote_plus(password)
    DATABASE_URI = f'postgresql://{user}:{encoded_password}@10.10.12.4:5432/MinvoiceCloud'
    ERROR_INVOICE_FOLDER = "error_invoice"
    APP_LOG_FOLDER = "applog"
    LOOP_JOB_INTERVAL = 300
    JOB_TIMEOUT = 2*60*60
