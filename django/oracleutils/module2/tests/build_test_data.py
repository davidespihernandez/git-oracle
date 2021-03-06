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
        self.build_bunch_of_houses_using_pl()

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

    def build_bunch_of_houses_using_pl(self):
        log.info("Creating a bunch of houses using PL")
        total = 10
        for i in range(total):
            thing_id = self.call_pl('pl1.create_example_house',
                         kparams={
                             'person_name_p': 'muchas casas',
                             'detail': f'house {i}',
                         },
                         return_type=int)
            log.info(f"Created house {thing_id}")

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
    print("Calling PL")
    response = builder.call_pl('pl1.procedure1', params=["parametro 1"])
    print(f"Respuesta1 {response}")
    response = builder.call_pl('pl1.procedure1', kparams={"param1": "parametro 1"})
    print(f"Respuesta2 {response}")
    response = builder.call_pl('pl1.funcion1', params=["parametro 1"], return_type=str)
    print(f"Respuesta3 {response}")
    response = builder.call_pl('pl1.funcion1', kparams={"param1": "parametro 1"}, return_type=str)
    print(f"Respuesta4 {response}")

    if clear:
        builder.clear()
    builder.build()
