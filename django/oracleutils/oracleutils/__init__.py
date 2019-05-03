from django.test.runner import DiscoverRunner

from module1 import TABLES as MODULE1_TABLES
from module2 import TABLES as MODULE2_TABLES

ALL_TABLES = {
    'module1': MODULE1_TABLES,
    'module2': MODULE2_TABLES,
}


class NoDbTestRunner(DiscoverRunner):
    """ A test runner to test without database creation/deletion """

    def setup_databases(self, **kwargs):
        pass

    def teardown_databases(self, old_config, **kwargs):
        pass
