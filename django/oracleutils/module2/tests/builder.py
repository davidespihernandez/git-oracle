import logging
from module2.factories.car import CarFactory
from module2.factories.house import HouseFactory
from module2.factories.person import PersonFactory
from module2.factories.thing import ThingFactory
from module2.models.thing_type import ThingType

log = logging.getLogger('oracleutils')


class Builder:

    def __init__(self):
        self.thing_types_props = {
            'CAR': {'name': 'Car'},
            'HOU': {'name': 'House'},
        }

    def person(self, **kwargs):
        return PersonFactory(**kwargs)

    def thing(self, person=None, thing_type='CAR'):
        log.info(f"Building thing {thing_type}")
        # hacer función cacheada para esto
        thing_type_object = ThingType.objects.get_or_create(
            thing_type_code=thing_type,
            name=self.thing_types_props[thing_type]['name'],
        )[0]
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

