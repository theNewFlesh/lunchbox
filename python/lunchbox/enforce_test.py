import unittest

import pytest

from lunchbox.enforce import Comparator, Enforce, EnforceError
# ------------------------------------------------------------------------------


class ComparatorTests(unittest.TestCase):
    def test_init(self):
        result = Comparator.SIMILAR
        self.assertEqual(result.function, 'similar')
        self.assertEqual(result.text, 'similar')
        self.assertEqual(result.symbol, '~')
        self.assertEqual(result.negation, False)
        self.assertEqual(result.negation_symbol, '!~')
        self.assertEqual(result.message, 'not similar to')

    def test_canonical(self):
        result = Comparator.SIMILAR.canonical
        self.assertEqual(result, 'similar')

        result = Comparator.NOT_EQ.canonical
        self.assertEqual(result, 'not_eq')

    def test_from_string(self):
        self.assertEqual(Comparator.from_string('equal'), Comparator.EQ)
        self.assertEqual(Comparator.from_string('=='), Comparator.EQ)
        self.assertEqual(Comparator.from_string('not equal'), Comparator.NOT_EQ)
        self.assertEqual(Comparator.from_string('!='), Comparator.NOT_EQ)
        self.assertEqual(Comparator.from_string('greater'), Comparator.GT)
        self.assertEqual(Comparator.from_string('>'), Comparator.GT)
        self.assertEqual(Comparator.from_string('greater or equal'), Comparator.GTE)
        self.assertEqual(Comparator.from_string('>='), Comparator.GTE)
        self.assertEqual(Comparator.from_string('lesser'), Comparator.LT)
        self.assertEqual(Comparator.from_string('<'), Comparator.LT)
        self.assertEqual(Comparator.from_string('lesser or equal'), Comparator.LTE)
        self.assertEqual(Comparator.from_string('<='), Comparator.LTE)
        self.assertEqual(Comparator.from_string('similar'), Comparator.SIMILAR)
        self.assertEqual(Comparator.from_string('~'), Comparator.SIMILAR)
        self.assertEqual(Comparator.from_string('not similar'), Comparator.NOT_SIMILAR)
        self.assertEqual(Comparator.from_string('!~'), Comparator.NOT_SIMILAR)
        self.assertEqual(Comparator.from_string('in'), Comparator.IN)
        self.assertEqual(Comparator.from_string('in'), Comparator.IN)
        self.assertEqual(Comparator.from_string('not in'), Comparator.NOT_IN)
        self.assertEqual(Comparator.from_string('not in'), Comparator.NOT_IN)
        self.assertEqual(Comparator.from_string('instance of'), Comparator.INSTANCE_OF)
        self.assertEqual(Comparator.from_string('isinstance'), Comparator.INSTANCE_OF)
        self.assertEqual(Comparator.from_string('not instance of'), Comparator.NOT_INSTANCE_OF)
        self.assertEqual(Comparator.from_string('not isinstance'), Comparator.NOT_INSTANCE_OF)


class EnforceTests(unittest.TestCase):
    def setUp(self):
        class Foo:
            def __init__(self, value):
                self.value = value

            def __repr__(self):
                return '<Foo>'

        class Bar:
            def __init__(self, value):
                self.value = value

            def __repr__(self):
                return '<Bar>'

        class EnforceFooBar(Enforce):
            def get_value(self, item):
                return item.value

        class Food:
            pass

        class Taco(Food):
            pass

        self.Foo = Foo
        self.Bar = Bar
        self.EnforceFooBar = EnforceFooBar
        self.Food = Food
        self.Taco = Taco

    # INIT----------------------------------------------------------------------
    def test_init_eq(self):
        Foo = self.Foo
        Bar = self.Bar
        EnforceFooBar = self.EnforceFooBar

        EnforceFooBar(Foo(1), '==', Bar(1), 'value')

        expected = 'value of <Foo> is not equal to value of <Bar>. 1 != 2.'
        with self.assertRaisesRegex(EnforceError, expected):
            EnforceFooBar(Foo(1), 'equal', Bar(2), 'value')

    def test_init_not_eq(self):
        Foo = self.Foo
        Bar = self.Bar
        EnforceFooBar = self.EnforceFooBar

        EnforceFooBar(Foo(1), '!=', Bar(2), 'value')

        expected = 'value of <Foo> is equal to value of <Bar>. 1 == 1.'
        with self.assertRaisesRegex(EnforceError, expected):
            EnforceFooBar(Foo(1), 'not equal', Bar(1), 'value')

    def test_init_gt(self):
        Foo = self.Foo
        Bar = self.Bar
        EnforceFooBar = self.EnforceFooBar

        EnforceFooBar(Foo(2), '>', Bar(1), 'value')

        expected = 'value of <Foo> is not greater than value of <Bar>. 1 <= 1.'
        with self.assertRaisesRegex(EnforceError, expected):
            EnforceFooBar(Foo(1), 'greater', Bar(1), 'value')

    def test_init_gte(self):
        Foo = self.Foo
        Bar = self.Bar
        EnforceFooBar = self.EnforceFooBar

        EnforceFooBar(Foo(1), '>=', Bar(1), 'value')

        expected = 'value of <Foo> is less than value of <Bar>. 1 < 2.'
        with self.assertRaisesRegex(EnforceError, expected):
            EnforceFooBar(Foo(1), 'greater or equal', Bar(2), 'value')

    def test_init_lt(self):
        Foo = self.Foo
        Bar = self.Bar
        EnforceFooBar = self.EnforceFooBar

        EnforceFooBar(Foo(1), '<', Bar(2), 'value')

        expected = 'value of <Foo> is not less than value of <Bar>. 1 >= 1.'
        with self.assertRaisesRegex(EnforceError, expected):
            EnforceFooBar(Foo(1), 'lesser', Bar(1), 'value')

    def test_init_lte(self):
        Foo = self.Foo
        Bar = self.Bar
        EnforceFooBar = self.EnforceFooBar

        EnforceFooBar(Foo(1), '<=', Bar(1), 'value')

        expected = 'value of <Foo> is greater than value of <Bar>. 2 > 1.'
        with self.assertRaisesRegex(EnforceError, expected):
            EnforceFooBar(Foo(2), 'lesser or equal', Bar(1), 'value')

    def test_init_similar(self):
        Foo = self.Foo
        Bar = self.Bar
        EnforceFooBar = self.EnforceFooBar

        EnforceFooBar(Foo(1), '~', Bar(2), 'value', epsilon=2)

        expected = 'value of <Foo> is not similar to value of <Bar>. Delta 1 is'
        expected += ' greater than epsilon 1.'
        with self.assertRaisesRegex(EnforceError, expected):
            EnforceFooBar(Foo(1), 'similar', Bar(2), 'value', epsilon=1)

    def test_init_not_similar(self):
        Foo = self.Foo
        Bar = self.Bar
        EnforceFooBar = self.EnforceFooBar

        EnforceFooBar(Foo(1), '!~', Bar(2), 'value', epsilon=1)

        expected = 'value of <Foo> is similar to value of <Bar>. Delta 1 is'
        expected += ' not greater than epsilon 2.'
        with self.assertRaisesRegex(EnforceError, expected):
            EnforceFooBar(Foo(1), 'not similar', Bar(2), 'value', epsilon=2)

    def test_init_in(self):
        Foo = self.Foo
        Bar = self.Bar
        EnforceFooBar = self.EnforceFooBar

        # regular
        Enforce('foo', 'in', ['foo', 'bar'])

        expected = r"foo is not in \['boo', 'bar'\]\."
        with self.assertRaisesRegex(EnforceError, expected):
            Enforce('foo', 'in', ['boo', 'bar'])

        # attribute
        EnforceFooBar(Foo(1), 'in', [Bar(1), Foo(2)], 'value')

        expected = r"value of <Foo> is not in value of \[<Bar>, <Bar>\]\."
        with self.assertRaisesRegex(EnforceError, expected):
            EnforceFooBar(Foo(1), 'in', [Bar(2), Bar(3)], 'value')

    def test_init_not_in(self):
        Foo = self.Foo
        Bar = self.Bar
        EnforceFooBar = self.EnforceFooBar

        # regular
        Enforce('foo', 'not in', ['taco', 'bar'])

        expected = r"foo is in \['foo', 'bar'\]\."
        with self.assertRaisesRegex(EnforceError, expected):
            Enforce('foo', 'not in', ['foo', 'bar'])

        # attribute
        EnforceFooBar(Foo(1), 'not in', [Bar(2), Foo(2)], 'value')

        expected = r"value of <Foo> is in value of \[<Bar>, <Bar>\]\."
        with self.assertRaisesRegex(EnforceError, expected):
            EnforceFooBar(Foo(1), 'not in', [Bar(1), Bar(3)], 'value')

    def test_init_instance_of(self):
        Food = self.Food
        Taco = self.Taco

        Enforce(1, 'instance of', int)
        Enforce(Taco(), 'instance of', Food)

        expected = r'1 is not instance of \[.*str.*, .*float.*\]\.'
        with self.assertRaisesRegex(EnforceError, expected):
            Enforce(1, 'instance of', [str, float])

    def test_init_not_instance_of(self):
        Food = self.Food
        Taco = self.Taco

        Enforce(1, 'not instance of', float)
        Enforce(Taco(), 'not instance of', Exception)

        expected = r'1 is instance of \[.*int.*, .*float.*\]\.'
        with self.assertRaisesRegex(EnforceError, expected):
            Enforce(1, 'not instance of', [int, float])

        expected = r'.*Taco.* is instance of \[.*Food.*, .*float.*\]\.'
        with self.assertRaisesRegex(EnforceError, expected):
            Enforce(Taco(), 'not instance of', [Food, float])

    # MESSAGE-------------------------------------------------------------------
    def test_init_message(self):
        Foo = self.Foo
        Bar = self.Bar
        EnforceFooBar = self.EnforceFooBar

        msg = '{a} is not like {b}. Please adjust your epsilon: {epsilon}, '
        msg += 'to be higher than {delta}. '
        msg += 'A value: {a_val}. B value: {b_val}.'

        a = Foo(1)
        b = Bar(5)
        epsilon = 2

        with pytest.raises(EnforceError) as e:
            EnforceFooBar(a, '~', b, 'value', epsilon=epsilon, message=msg)
        expected = msg.format(
            a=a, b=b, epsilon=epsilon, delta=4, a_val=1, b_val=5
        )
        self.assertEqual(str(e.value), expected)

    def test_get_message_no_attribute(self):
        e = Enforce(1, '==', 1)
        result = e._get_message(None, Comparator.EQ)
        expected = '{a} is {comparator.message} {b}.'
        expected += ' {a_val} {comparator.negation_symbol} {b_val}.'
        self.assertEqual(result, expected)

    def test_get_message_attribute(self):
        e = Enforce(1, '==', 1)
        result = e._get_message('foo', Comparator.EQ)
        expected = '{attribute} of {a} is {comparator.message} {attribute} of '
        expected += '{b}. {a_val} {comparator.negation_symbol} {b_val}.'
        self.assertEqual(result, expected)

    def test_get_message_skip(self):
        e = Enforce(1, '==', 1)
        skip = [
            Comparator.IN,
            Comparator.NOT_IN,
            Comparator.INSTANCE_OF,
            Comparator.NOT_INSTANCE_OF,
        ]

        expected = '{a} is {comparator.message} {b}.'
        for item in skip:
            result = e._get_message(None, item)
            self.assertEqual(result, expected)

        expected = '{attribute} of {a} is {comparator.message} {attribute} of {b}.'
        for item in skip:
            result = e._get_message('foo', item)
            self.assertEqual(result, expected)

    def test_get_message_similar(self):
        e = Enforce(1, '==', 1)
        result = e._get_message('foo', Comparator.SIMILAR)
        expected = '{attribute} of {a} is {comparator.message} {attribute} of '
        expected += '{b}. Delta {delta} is greater than epsilon {epsilon}.'
        self.assertEqual(result, expected)

    def test_get_message_not_similar(self):
        e = Enforce(1, '==', 1)
        result = e._get_message('foo', Comparator.NOT_SIMILAR)
        expected = '{attribute} of {a} is {comparator.message} {attribute} of '
        expected += '{b}. Delta {delta} is not greater than epsilon {epsilon}.'
        self.assertEqual(result, expected)

    # COMPARATORS---------------------------------------------------------------
    def test_eq(self):
        e = Enforce(1, '==', 1)
        self.assertTrue(e.eq(1, 1))
        self.assertFalse(e.eq(1, 2))

    def test_gt(self):
        e = Enforce(1, '==', 1)
        self.assertTrue(e.gt(2, 1))
        self.assertFalse(e.gt(1, 1))
        self.assertFalse(e.gt(1, 2))

    def test_gte(self):
        e = Enforce(1, '==', 1)
        self.assertTrue(e.gte(2, 1))
        self.assertTrue(e.gte(1, 1))
        self.assertFalse(e.gte(1, 2))

    def test_lt(self):
        e = Enforce(1, '==', 1)
        self.assertTrue(e.lt(1, 2))
        self.assertFalse(e.lt(1, 1))
        self.assertFalse(e.lt(2, 1))

    def test_lte(self):
        e = Enforce(1, '==', 1)
        self.assertTrue(e.lte(1, 2))
        self.assertTrue(e.lte(1, 1))
        self.assertFalse(e.lte(2, 1))

    def test_similar(self):
        e = Enforce(1, '==', 1)
        self.assertTrue(e.similar(0.9, epsilon=1))
        self.assertFalse(e.similar(1.0, epsilon=1))
        self.assertFalse(e.similar(1.1, epsilon=1))

    def test_difference(self):
        e = Enforce(1, '==', 1)
        self.assertEqual(e.difference(1, 2), 1)
        self.assertEqual(e.difference(3, 2), 1)

    def test_in(self):
        e = Enforce(1, '==', 1)
        self.assertTrue(e.in_(1, [1, 2]))
        self.assertFalse(e.in_(1, [2, 3]))

    def test_instance_of(self):
        e = Enforce(1, '==', 1)
        self.assertTrue(e.instance_of(1, int))
        self.assertFalse(e.instance_of(1, str))
        self.assertTrue(e.instance_of(1, [int, float]))
        self.assertFalse(e.instance_of(1, [str, dict]))
        self.assertTrue(e.instance_of(1, tuple([int, float])))
        self.assertFalse(e.instance_of(1, tuple([str, dict])))

    # GETTERS-------------------------------------------------------------------
    def test_get_type_name(self):
        e = Enforce(1, '==', 1)
        Taco = self.Taco
        expected = Taco().__class__.__name__
        result = e.get_type_name(Taco())
        self.assertEqual(result, expected)
