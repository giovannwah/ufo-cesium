from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting content type objects...')
        ContentType.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Deleted.'))
