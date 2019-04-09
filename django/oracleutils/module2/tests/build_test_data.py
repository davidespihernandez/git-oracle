import logging

from django.db import transaction

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

    @transaction.atomic()
    def build(self):
        log.info("Building test data for module 2")
        self.build_people()
        self.build_things()

    def build_people(self):
        log.info("Building people")
        self.person_no_things = self.builder.person(name='No things')
        self.person_car = self.builder.person(name='Car')
        self.person_house = self.builder.person(name='House')
        self.person_both = self.builder.person(name='Both')

    def build_things(self):
        log.info("Building things")
        self.builder.car(person=self.person_car, detail='Car Make')
        log.info("Building things 1")
        self.builder.house(person=self.person_house, detail='House address')
        log.info("Building things 2")
        self.builder.car(person=self.person_both, detail='Car Make')
        log.info("Building things 3")
        self.builder.house(person=self.person_both, detail='House address')

    @transaction.atomic()
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
