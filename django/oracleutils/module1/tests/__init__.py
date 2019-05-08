from module1.tests.build_test_data import TestDataBuilder
from module1.tests.builder import Builder
from oracleutils.tests import BaseTestCase


class Module1TestCase(BaseTestCase):
    module = 'module1'
    helper = TestDataBuilder()
    builder = Builder()
