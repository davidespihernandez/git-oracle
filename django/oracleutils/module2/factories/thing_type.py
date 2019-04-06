from module2.models.thing_type import ThingType
from oracleutils.factories.base import BaseFactory


class ThingTypeFactory(BaseFactory):
    class Meta:
        model = ThingType
        django_get_or_create = ('thing_type_code', )

    thing_type_code = 'CAR'
    name = 'Car'
