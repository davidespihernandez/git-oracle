import logging

from module2.models.car import Car
from module2.models.house import House
from module2.models.person import Person
from module2.models.thing import Thing
from module2.models.thing_type import ThingType
from module2.tests.builder import Builder
from oracleutils.builder.base import BaseDataBuilder

log = logging.getLogger('oracleutils')


class TestDataBuilder(BaseDataBuilder):
    builder = Builder()

    def build(self):
        log.info("Building test data for module 2")
        self.build_people()

    def build_people(self):
        log.info("Building people")
        self.builder.person()

    def clear(self):
        log.info("Clearing data for module 2 ")
        Car.objects.all().delete()
        House.objects.all().delete()
        Thing.objects.all().delete()
        Person.objects.all().delete()
        ThingType.objects.all().delete()


def build_test_data(clear=True):
    builder = TestDataBuilder()
    if clear:
        builder.clear()
    builder.build()
