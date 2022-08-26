from os import environ

from dotenv import load_dotenv

load_dotenv()

PAYPAL_WEBHOOK_ID = environ["PAYPAL_WEBHOOK_ID"]
