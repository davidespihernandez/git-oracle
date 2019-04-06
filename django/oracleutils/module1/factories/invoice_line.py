import factory

from module1.factories.invoice import InvoiceFactory
from module1.models.invoice_line import InvoiceLine
from oracleutils.factories.base import BaseFactory


class InvoiceLineFactory(BaseFactory):
    class Meta:
        model = InvoiceLine

    invoice_line_id = factory.Sequence(lambda n: -n)
    invoice = factory.SubFactory(InvoiceFactory)
    detail = factory.Faker('text', locale='es_ES')

