from module2.factories.person import PersonFactory


class Builder:
    def person(self, **kwargs):
        return PersonFactory(**kwargs)
