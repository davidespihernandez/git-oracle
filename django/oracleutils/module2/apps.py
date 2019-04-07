from django.apps import AppConfig


class Module2Config(AppConfig):
    name = 'module2'

    def create_test_data(self, *args, clear=True, **kwargs):
        from .tests.build_test_data import build_test_data
        build_test_data(clear=clear)

