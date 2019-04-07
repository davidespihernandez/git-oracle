import logging

from module1.models.customer import Customer
from module1.models.invoice import Invoice
from module1.models.invoice_line import InvoiceLine
from module1.tests.builder import Builder
from oracleutils.builder.base import BaseDataBuilder

log = logging.getLogger('oracleutils')


class TestDataBuilder(BaseDataBuilder):
    builder = Builder()

    def build(self):
        log.info("Building test data for module 1")
        self.build_customers()

    def build_customers(self):
        log.info("Building customers")
        self.builder.customer()

    def clear(self):
        log.info("Clearing data for module 1 ")
        InvoiceLine.objects.all().delete()
        Invoice.objects.all().delete()
        Customer.objects.all().delete()


def build_test_data(clear=True):
    builder = TestDataBuilder()
    if clear:
        builder.clear()
    builder.build()
