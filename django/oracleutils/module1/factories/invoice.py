import factory

from datetime import datetime
from module1.factories.customer import CustomerFactory
from module1.models.invoice import Invoice
from oracleutils.factories.base import BaseFactory


class InvoiceFactory(BaseFactory):
    class Meta:
        model = Invoice

    invoice_id = factory.Sequence(lambda n: -n)
    customer = factory.SubFactory(CustomerFactory)
    date_created = factory.LazyFunction(datetime.now)
