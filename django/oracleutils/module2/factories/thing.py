from datetime import datetime

import factory

from module2.factories.person import PersonFactory
from module2.factories.thing_type import ThingTypeFactory
from module2.models.thing import Thing


class ThingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Thing
        django_get_or_create = ('person', 'thing_type_code', )

    thing_id = factory.Sequence(lambda n: -n)
    person = factory.SubFactory(PersonFactory)
    date_created = factory.LazyFunction(datetime.now)
    thing_type_code = factory.SubFactory(ThingTypeFactory)
