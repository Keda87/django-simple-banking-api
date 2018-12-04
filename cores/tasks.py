from celery import shared_task
from pymongo import MongoClient
from datetime import datetime


client = MongoClient('secondary_db', 27017)
db = client['banking']
transaction_logs = db.transaction_logs


@shared_task(bind=True)
def task_event_logging(self, log_dict: dict):
    log_dict.update({'created': datetime.utcnow()})
    transaction_logs.insert_one(log_dict)