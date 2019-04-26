from django.db import connection


class BaseDataBuilder:
    def build(self):
        raise NotImplemented

    def clear(self):
        raise NotImplemented

    def call_pl(self, package_and_method, parameters):
        cursor = connection.cursor()
        ret = cursor.callproc(package_and_method, parameters)
        cursor.close()
        return ret

    class Meta:
        abstract = True
