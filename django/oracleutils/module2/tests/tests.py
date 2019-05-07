from datetime import datetime

from django.test import TestCase

from module2.tests.build_test_data import TestDataBuilder


class BaseTestCase(TestCase):
    def test_dummy(self):
        self.assertEqual(1, 1)

    def test_call_pl(self):
        builder = TestDataBuilder()
        today = datetime.today()
        today_str = today.strftime('%d/%m/%Y')
        calls = [
            {
                'name': 'call with TRUE',
                'arguments': {
                    'varchar2_p': 'cadena',
                    'number_p': 1,
                    'boolean_p': True,
                    'date_p': today,
                },
                'expected': f'cadena-1-TRUE-{today_str}',
            },
            {
                'name': 'call with FALSE',
                'arguments': {
                    'varchar2_p': 'cadena',
                    'number_p': 1,
                    'boolean_p': False,
                    'date_p': today,
                },
                'expected': f'cadena-1-FALSE-{today_str}',
            },
        ]
        for call in calls:
            with self.subTest(call['name']):
                result = builder.call_pl(
                    package_and_method='pl1.different_types_args',
                    kparams=call['arguments'],
                    return_type=str,
                )
                self.assertEqual(
                    result,
                    call['expected'],
                )
