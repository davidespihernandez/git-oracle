import functools
import logging
from module2.factories.car import CarFactory
from module2.factories.house import HouseFactory
from module2.factories.person import PersonFactory
from module2.factories.thing import ThingFactory
from module2.factories.thing_type import ThingTypeFactory
from module2.tests.master_tables import MasterTables

log = logging.getLogger('oracleutils')


class Builder:
    @functools.lru_cache(maxsize=128)
    def get_thing_type(self, thing_type_code):
        data = MasterTables.THING_TYPE[thing_type_code]
        if data:
            return ThingTypeFactory(**data)
        return None

    def person(self, **kwargs):
        return PersonFactory(**kwargs)

    def thing(self, person=None, thing_type='CAR'):
        log.info(f"Building thing {thing_type}")
        thing_type_object = self.get_thing_type(thing_type)
        thing = ThingFactory(
            person=person or self.person(),
            thing_type_code=thing_type_object,
        )
        return thing

    def house(self, person=None, detail=None):
        person = person or self.person()
        log.info(f"building house for {person}")
        thing = self.thing(person=person, thing_type='HOU')
        house_args = {
            'thing': thing,
        }
        if detail:
            house_args['detail'] = detail
        return HouseFactory(**house_args)

    def car(self, person=None, detail=None):
        person = person or self.person()
        log.info(f"building car for {person}")
        thing = self.thing(person=person, thing_type='CAR')
        car_args = {
            'thing': thing,
        }
        if detail:
            car_args['detail'] = detail
        return CarFactory(**car_args)

