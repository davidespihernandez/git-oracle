from contextlib import redirect_stdout

from django.core.management.base import BaseCommand
from django.core.management.commands.inspectdb import (
    Command as InspectDbCommand,
)

from oracleutils import ALL_TABLES


class Command(BaseCommand):
    help = 'Crear modelos a partir de la base de datos Oracle'

    def handle(self, *args, **options):
        for app, tables in ALL_TABLES.items():
            with open(f'{app}/models/__init__.py', 'w') as init_file:
                for table in tables:
                    table_name = table.lower()
                    with open(f'{app}/models/{table_name}.py', 'w') as f:
                        with redirect_stdout(f):
                            InspectDbCommand().execute(
                                table=[table],
                                database='default',
                                no_color=True,
                            )
                    init_file.write(f'from .{table_name} import *\n')
