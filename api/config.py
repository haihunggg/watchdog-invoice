from urllib.parse import quote_plus


class Config:
    user = "postgres"
    password = "Jarvis@123!@#"
    encoded_password = quote_plus(password)
    DATABASE_URI = f'postgresql://{user}:{encoded_password}@10.10.12.4:5432/MinvoiceCloud'
    ERROR_INVOICE_FOLDER = r"E:\watchdog-invoice\console\error_invoice"
    SECRET_KEY = "hungth_minvoice@123"
