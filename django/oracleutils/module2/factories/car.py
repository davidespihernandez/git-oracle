import factory

from module2.factories.thing import ThingFactory
from module2.models.car import Car
from oracleutils.factories.base import BaseFactory


class CarFactory(BaseFactory):
    class Meta:
        model = Car

    thing = factory.SubFactory(ThingFactory)
    detail = factory.Faker('text', locale='es_ES')
