from django.db import connection


class BaseDataBuilder:
    def build(self):
        raise NotImplemented

    def clear(self):
        raise NotImplemented

    def call_pl(self, package_and_method, params=None, kparams=None, return_type=None):
        if params is None:
            params = []
        if kparams is None:
            kparams = {}
        cursor = connection.cursor()
        if return_type:
            ret = cursor.callfunc(package_and_method, return_type, parameters=params, keywordParameters=kparams)
        else:
            ret = cursor.callproc(package_and_method, params=params, kparams=kparams)
        cursor.close()
        return ret

    class Meta:
        abstract = True
