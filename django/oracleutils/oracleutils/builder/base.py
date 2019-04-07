class BaseDataBuilder:
    def build(self):
        raise NotImplemented

    def clear(self):
        raise NotImplemented

    class Meta:
        abstract = True
