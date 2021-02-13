from user.models import User
import datetime
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

now = datetime.datetime.now()
timeout_h = 24
delta = now - datetime.timedelta(hours=timeout_h)

class Command(BaseCommand):
    def handle(self, *args, **options):
        no_actives = User.objects.filter(is_active=False, date_joined__lt=delta).all()
        no_actives.delete()
        self.stdout.write(self.style.SUCCESS('success'))