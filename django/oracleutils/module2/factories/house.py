import factory

from module2.factories.thing import ThingFactory
from module2.models.house import House
from oracleutils.factories.base import BaseFactory


class HouseFactory(BaseFactory):
    class Meta:
        model = House

    thing = factory.SubFactory(ThingFactory)
    detail = factory.Faker('text', locale='es_ES')
