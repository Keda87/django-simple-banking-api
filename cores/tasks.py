from celery import shared_task


@shared_task(bind=True)
def task_event_logging(self, message):
    pass