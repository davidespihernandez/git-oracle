import factory


class BaseFactory(factory.django.DjangoModelFactory):
    @classmethod
    def _setup_next_sequence(cls):
        return cls._meta.model.objects.count() + 1
