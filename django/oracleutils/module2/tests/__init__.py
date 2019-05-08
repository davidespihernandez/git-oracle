from module2.tests.build_test_data import TestDataBuilder
from module2.tests.builder import Builder
from oracleutils.tests import BaseTestCase


class Module2TestCase(BaseTestCase):
    module = 'module2'
    helper = TestDataBuilder()
    builder = Builder()
