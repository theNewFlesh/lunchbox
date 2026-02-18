from enum import Enum
import unittest

import lunchbox.enum as lbe
# ------------------------------------------------------------------------------


class FooEnum(lbe.EnumBase):
    A = 'a'
    B = 'b'
    C = 'c'


class BarEnum(lbe.EnumBase):
    A = ('a', 'yup')
    B = ('b', 'yup')
    C = ('c', 'yup')


class ABCEnum(lbe.EnumBase):
    A = 'a'
    B = 'b'
    C = 'c'
    A_B_C = 'a-b-c'
    D_E_F = 'd_e_f'


class EnumBaseMetaTests(unittest.TestCase):
    def test_repr(self):
        class Foo(Enum, metaclass=lbe.EnumBaseMeta):
            pass

        self.assertEqual(repr(Foo), 'Foo')


class EnumBaseTests(unittest.TestCase):
    def test_to_dict(self):
        class TestEnum(lbe.EnumBase):
            FOO = 'foo'
            BAR = 'bar'

        result = TestEnum.to_dict()
        expected = dict(FOO='foo', BAR='bar')
        self.assertEqual(result, expected)

    def test_from_string(self):
        self.assertIs(FooEnum.from_string('a'), FooEnum.A)
        self.assertIs(FooEnum.from_string('b'), FooEnum.B)
        self.assertIs(FooEnum.from_string('c'), FooEnum.C)

    def test_from_string_error(self):
        expected = 'pizza is not a legal FooEnum string. '
        expected += 'Legal options: a, b, c.'
        with self.assertRaisesRegex(ValueError, expected):
            FooEnum.from_string('pizza')

    def test_options(self):
        self.assertEqual(FooEnum.options(), list('abc'))
        self.assertEqual(BarEnum.options(), list('abc'))

    def test_members(self):
        expected = [FooEnum.A, FooEnum.B, FooEnum.C]
        result = FooEnum.members()
        self.assertCountEqual(result, expected)
        for r, e in zip(result, expected):
            self.assertIs(r, e)

    def test_repr(self):
        self.assertEqual(repr(FooEnum.A), 'FooEnum.A')
