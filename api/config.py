from urllib.parse import quote_plus


class Config:
    user = "minvoice"
    password = "Minvoice@123"
    encoded_password = quote_plus(password)
    DATABASE_URI = f'postgresql://{user}:{encoded_password}@103.61.122.194:5432/MinvoiceCloud'
    ERROR_INVOICE_FOLDER = r"E:\watchdog-invoice\api-release\console\error_invoice"
    SECRET_KEY = "hungth_minvoice@123"
