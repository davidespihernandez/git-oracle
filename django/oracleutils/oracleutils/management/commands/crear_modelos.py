from contextlib import redirect_stdout

from django.core.management.base import BaseCommand
from django.core.management.commands.inspectdb import (
    Command as InspectDbCommand,
)

from comandos import ALL_TABLES


class Command(BaseCommand):
    help = 'Crear modelos a partir de la base de datos Oracle, para este módulo'

    def handle(self, *args, **options):
        for app, tables in ALL_TABLES.items():
            for table in tables:
                with open(f'{app}/models/{table.lower()}.py', 'w') as f:
                    with redirect_stdout(f):
                        InspectDbCommand().execute(
                            table=[table],
                            database='default',
                            no_color=True,
                        )
