from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Genera los datos de test para cada módulo.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--noclear',
            action='store_false',  # por defecto a True...
            dest='clear',
            help='No borrar el contenido de las tablas antes de generar datos'
                 ' (por defecto se borra).'
        )

    @transaction.atomic
    def handle(self, *args, clear=True, **options):
        # Execute the create_test_data
        for config in apps.get_app_configs():
            if hasattr(config, 'create_test_data'):
                config.create_test_data(clear=clear)
