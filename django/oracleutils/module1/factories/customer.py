import factory
from module1.models.customer import Customer
from oracleutils.factories.base import BaseFactory


class CustomerFactory(BaseFactory):
    class Meta:
        model = Customer
        django_get_or_create = ('name', )

    customer_id = factory.Sequence(lambda n: -n)
    name = factory.Faker('name', locale='es_ES')
