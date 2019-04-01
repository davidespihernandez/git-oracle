import factory
from module2.models.thing_type import ThingType


class ThingTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ThingType
        django_get_or_create = ('thing_type_code', )

    thing_type_code = 'CAR'
    name = 'Car'
