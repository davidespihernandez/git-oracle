import logging

from module1.tests.builder import Builder

log = logging.getLogger(__name__)


class TestDataBuilder:
    builder = Builder()

    def build(self):
        log.info("Building test data for module 1")
        self.build_customers()

    def build_customers(self):
        log.info("Building customers")
        self.builder.customer()


def build_test_data():
    builder = TestDataBuilder()
    builder.build()
