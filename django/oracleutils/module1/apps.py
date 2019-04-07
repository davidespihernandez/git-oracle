from django.apps import AppConfig


class Module1Config(AppConfig):
    name = 'module1'

    def create_test_data(self, *args, clear=True, **kwargs):
        from .tests.build_test_data import build_test_data
        build_test_data(clear=clear)

