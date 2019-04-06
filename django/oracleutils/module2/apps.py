from django.apps import AppConfig


class Module2Config(AppConfig):
    name = 'module2'
    cargar = True

    def create_test_data(self, *args, **kwargs):
        from .tests.build_test_data import build_test_data
        build_test_data()

