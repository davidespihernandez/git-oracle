from datetime import datetime

from module2.tests import Module2TestCase


class DummyTestCase(Module2TestCase):
    def test_dummy(self):
        self.assertEqual(1, 1)

    def test_call_pl(self):
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
                result = self.helper.call_pl(
                    package_and_method='pl1.different_types_args',
                    kparams=call['arguments'],
                    return_type=str,
                )
                self.assertEqual(
                    result,
                    call['expected'],
                )


class CountThingsTestCase(Module2TestCase):
    def setUp(self):
        self.person = self.builder.person()

    # No es necesario un tearDown, porque cada test es una transacción de la
    # que se hace rollback, pero aquí va un ejemplo

    # def tearDown(self):
    #     self.person.thing_set.all().delete()
    #     self.person.delete()

    def perform_call(self):
        return self.helper.call_pl(
            package_and_method='pl1.count_person_things',
            params=[self.person.person_id],
            return_type=int,
        )

    def test_person_with_things(self):
        things_number = 3
        for i in range(things_number):
            self.builder.thing(person=self.person)

        self.assertEqual(
            self.perform_call(),
            things_number,
        )

    def test_person_without_things(self):
        self.assertEqual(
            self.perform_call(),
            0,
        )
