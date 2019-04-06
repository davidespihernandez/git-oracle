from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Borra los datos de la base de datos y genera los datos de test' \
           ' para cada módulo.'

    @transaction.atomic
    def handle(self, *args, **options):
        # Delete the database data
        call_command('flush', interactive=False)
        print("After flush ")
        # Execute the create_test_data
        for config in apps.get_app_configs():
            if hasattr(config, 'create_test_data'):
                print("Creating ")
                config.create_test_data()
