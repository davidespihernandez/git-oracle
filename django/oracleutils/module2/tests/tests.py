from django.test import SimpleTestCase


class BaseTestCase(SimpleTestCase):
    def test_dummy(self):
        self.assertEqual(1, 1)

    def test_dummy_2(self):
        self.assertEqual(1, 2)
