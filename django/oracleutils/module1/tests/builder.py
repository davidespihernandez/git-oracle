from module1.factories.customer import CustomerFactory


class Builder:
    def customer(self, **kwargs):
        return CustomerFactory(**kwargs)
