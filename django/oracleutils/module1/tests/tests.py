from unittest import TestCase

# Create your tests here.
from module1.tests.builder import Builder


class BuilderTestCase(TestCase):
    # def setUp(self):
    #     self.builder = Builder()

    def test_dummy(self):
        self.assertEqual(1, 1)

    # def test_create_customer_with_name(self):
    #     name = 'my name'
    #     customer = self.builder.customer_with_name(name=name)
    #     self.assertIsNotNone(customer)
    #     self.assertEqual(customer.name, name)
