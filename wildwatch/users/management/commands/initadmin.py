from users.models import CustomUser
from django.core.management.base import BaseCommand
import environ

env = environ.Env()


class Command(BaseCommand):
    def handle(self, *args, **options):
        if env.bool('CREATE_DJANGO_SUPERUSER', default=False):
            if CustomUser.objects.count() == 0:
                username = env.str('DJANGO_SUPERUSER_USERNAME', 'admin')
                email = env.str('DJANGO_SUPERUSER_EMAIL', '')
                password = env.str('DJANGO_SUPERUSER_PASSWORD', '123')
                admin = CustomUser.objects.create_superuser(email=email, username=username, password=password)
                admin.save()
                print('Created superuser {}'.format(username))
            else:
                print('Not created admin. Accounts already exist.')
