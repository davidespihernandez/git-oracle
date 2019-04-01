import factory
from module2.models.person import Person


class PersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Person
        django_get_or_create = ('name', )

    person_id = factory.Sequence(lambda n: -n)
    name = factory.Faker('name', locale='es_ES')
