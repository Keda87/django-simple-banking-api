from datetime import datetime

from celery import shared_task
from pymongo import MongoClient

client = MongoClient('secondary_db', 27017)
db = client['banking']
transaction_logs = db.transaction_logs


@shared_task
def task_event_logging(user_email: str, message: str, meta: dict):
    event_meta = {
        'created': datetime.utcnow(),
        'user_email': user_email,
        'description': message,
        'metadata': meta
    }
    transaction_logs.insert_one(event_meta)