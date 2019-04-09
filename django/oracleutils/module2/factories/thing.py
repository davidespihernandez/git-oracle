from datetime import datetime

import factory

from module2.factories.person import PersonFactory
from module2.factories.thing_type import ThingTypeFactory
from module2.models.thing import Thing
from oracleutils.factories.base import BaseFactory


class ThingFactory(BaseFactory):
    class Meta:
        model = Thing

    thing_id = factory.Sequence(lambda n: -n)
    person = factory.SubFactory(PersonFactory)
    date_created = factory.LazyFunction(datetime.now)
