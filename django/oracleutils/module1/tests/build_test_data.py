import logging

from django.db import transaction

from module1.models.customer import Customer
from module1.models.invoice import Invoice
from module1.models.invoice_line import InvoiceLine
from module1.tests.builder import Builder
from oracleutils.builder.base import BaseDataBuilder

log = logging.getLogger('oracleutils')


class TestDataBuilder(BaseDataBuilder):
    builder = Builder()

    @transaction.atomic()
    def build(self):
        log.info("Building test data for module 1")
        self.build_customers()
        self.build_invoices()

    def build_customers(self):
        log.info("Building customers")
        self.cust_no_inv = self.builder.customer_with_name(
            name='Without invoices')
        self.cust_inv_1_line = self.builder.customer_with_name(
            name='With invoice single line')
        self.cust_inv_3_lines = self.builder.customer_with_name(
            name='With invoice 3 lines')

    def build_invoices(self):
        log.info("Building invoices")
        self.builder.invoice_with_lines(
            totals=[10, ],
            customer=self.cust_inv_1_line,
        )
        self.builder.invoice_with_lines(
            totals=(10, 20, 30, ),
            details=('Detail 10', 'Detail 20', 'Detail 30', ),
            customer=self.cust_inv_3_lines,
        )

    @transaction.atomic()
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
