from django.test import TestCase


class BaseTestCase(TestCase):
    module = ''
    helper = None
    builder = None
