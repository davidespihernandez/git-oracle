import logging

from module2.tests.builder import Builder

log = logging.getLogger(__name__)


class TestDataBuilder:
    builder = Builder()

    def build(self):
        log.info("Building test data for module 2")
        self.build_people()

    def build_people(self):
        log.info("Building people")
        self.builder.person()


def build_test_data():
    builder = TestDataBuilder()
    builder.build()
