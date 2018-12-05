from django.core.management import BaseCommand

from cores.tasks import transaction_logs


class Command(BaseCommand):

    def handle(self, *args, **options):

        for log in transaction_logs.find():
            print(log)
