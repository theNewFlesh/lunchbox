import unittest

import lunchbox.infix as lbi
# ------------------------------------------------------------------------------


class LeftRight(int):
    def __init__(self, data):
        self.data = data

    def left(self, other):
        if hasattr(other, 'data'):
            other = other.data
        return (self.data, other)

    def right(self, other):
        if hasattr(other, 'data'):
            other = other.data
        return (other, self.data)


class Unary:
    def __init__(self, data):
        self.data = data

    def left(self):
        return 'not ' + str(self.data)


class FakeArithmeticInfix(lbi.ArithmeticInfix, LeftRight):
    def __init__(self, data):
        super().__init__(data)
        self.data = data
        self._infix_lookup.update({
            '+': 'left',
            'r+': 'right',
            '-': 'left',
            'r-': 'right',
            '*': 'left',
            'r*': 'right',
            '/': 'left',
            'r/': 'right',
        })


class FakeMathInfix(lbi.MathInfix, LeftRight):
    def __init__(self, data):
        super().__init__(data)
        self.data = data
        self._infix_lookup.update({
            '%': 'left',
            'r%': 'right',
            '//': 'left',
            'r//': 'right',
            '**': 'left',
            'r**': 'right',
            '@': 'left',
            'r@': 'right',
        })


class FakeLogicInfix(lbi.LogicInfix, LeftRight):
    def __init__(self, data):
        super().__init__(data)
        self.data = data
        self._infix_lookup.update({
            '&': 'left',
            'r&': 'right',
            '|': 'left',
            'r|': 'right',
            '^': 'left',
            'r^': 'right',
        })


class FakeComparisonInfix(lbi.ComparisonInfix, LeftRight):
    def __init__(self, data):
        super().__init__(data)
        self.data = data
        self._infix_lookup.update({
            '<': 'left',
            '<=': 'left',
            '>': 'left',
            '>=': 'left',
        })


class FakeBitwiseInfix(lbi.BitwiseInfix, LeftRight):
    def __init__(self, data):
        super().__init__(data)
        self.data = data
        self._infix_lookup.update({
            '>>': 'left',
            'r>>': 'right',
            '<<': 'left',
            'r<<': 'right',
        })


class FakeItemInfix(lbi.ItemInfix, LeftRight):
    def __init__(self, data):
        super().__init__(data)
        self.data = data
        self._infix_lookup.update({
            '[]': 'get',
            '[] =': 'set_',
            '[missing]': 'missing',
            'del []': 'delete',
        })

    def get(self, value):
        if value == 'missing':
            raise KeyError
        return self.data

    def set_(self, key, value):
        self.data = value
        return self

    def missing(self, value):
        return 'missing'

    def delete(self, value):
        self.data = None
        return self


class FakeUnaryInfix(lbi.UnaryInfix, Unary):
    def __init__(self, data):
        super().__init__(data)
        self.data = data
        self._infix_lookup.update({
            '~': 'left',
            'x-': 'left',
            'x+': 'left',
        })


class FakeEqualityInfix(lbi.EqualityInfix, LeftRight):
    def __init__(self, data):
        super().__init__(data)
        self.data = data
        self._infix_lookup.update({
            '==': 'left',
            '!=': 'left',
        })


class FakeAssignmentInfix(lbi.AssignmentInfix, LeftRight):
    def __init__(self, data):
        super().__init__(data)
        self.data = data
        self._infix_lookup.update({
            '+=': 'left',
            '-=': 'left',
            '*=': 'left',
            '/=': 'left',
            '%=': 'left',
            '//=': 'left',
            '**=': 'left',
            '@=': 'left',
            '&=': 'left',
            '|=': 'left',
            '^=': 'left',
            '>>=': 'left',
            '<<=': 'left',
        })


class FakeMiscInfix(lbi.MiscInfix):
    def __init__(self, data):
        super().__init__(data)
        self.data = data
        self._infix_lookup.update({
            'del .': 'del_',
            'in': 'in_',
        })

    def __iter__(self):
        return self

    def del_(self, value):
        self.data = None

    def in_(self, value):
        return True
# ------------------------------------------------------------------------------


class FakeInfix(lbi.ArithmeticInfix, int):
    def __init__(self, data):
        super().__init__(data)
        self._infix_lookup['+'] = 'add'
        self.data = data

    def add(self, value):
        return FakeInfix(self.data + value)


class FakeMonadInfix(lbi.ArithmeticInfix):
    def __init__(self, data):
        super().__init__(data)
        self._infix_lookup['+'] = 'add'
        self.data = data

    def add(self, value):
        return FakeMonadInfix(self.data + value.data)
# ------------------------------------------------------------------------------


class InfixBaseTests(unittest.TestCase):
    def test_init(self):
        result = lbi.InfixBase()
        self.assertEqual(result._infix_lookup, {})

    def test_get_infix_function(self):
        num = FakeInfix(9)
        result = num + 1
        self.assertEqual(result, 10)

    def test_get_infix_function_monad(self):
        a = FakeMonadInfix(9)
        b = FakeMonadInfix(1)
        result = a + b
        self.assertEqual(result.data, 10)

    def test_get_infix_function_error(self):
        fake = FakeInfix(9)
        fake._infix_lookup['foo'] = 'bar'
        expected = "Method bar not implemented for 'foo'."
        with self.assertRaisesRegex(NotImplementedError, expected):
            fake._get_infix_function('foo')

    def test_get_infix_function_error_symbol(self):
        expected = "Method not implemented for '-'."
        with self.assertRaisesRegex(NotImplementedError, expected):
            FakeInfix(9) - 1


class InfixTests(unittest.TestCase):
    def test_ArithmeticInfix(self):
        a = FakeArithmeticInfix(1)
        b = 2
        self.assertEqual(a + b, (1, 2))
        self.assertEqual(b + a, (2, 1))
        self.assertEqual(a - b, (1, 2))
        self.assertEqual(b - a, (2, 1))
        self.assertEqual(a * b, (1, 2))
        self.assertEqual(b * a, (2, 1))
        self.assertEqual(a / b, (1, 2))
        self.assertEqual(b / a, (2, 1))

    def test_MathInfix(self):
        a = FakeMathInfix(1)
        b = 2
        self.assertEqual(a % b, (1, 2))
        self.assertEqual(b % a, (2, 1))
        self.assertEqual(a // b, (1, 2))
        self.assertEqual(b // a, (2, 1))
        self.assertEqual(a ** b, (1, 2))
        self.assertEqual(b ** a, (2, 1))
        self.assertEqual(a @ b, (1, 2))
        self.assertEqual(b @ a, (2, 1))

    def test_LogicInfix(self):
        a = FakeLogicInfix(1)
        b = 2
        self.assertEqual(a & b, (1, 2))
        self.assertEqual(b & a, (2, 1))
        self.assertEqual(a | b, (1, 2))
        self.assertEqual(b | a, (2, 1))
        self.assertEqual(a ^ b, (1, 2))
        self.assertEqual(b ^ a, (2, 1))

    def test_ComparisonInfix(self):
        a = FakeComparisonInfix(1)
        b = 2
        self.assertEqual(a < b, (1, 2))
        self.assertEqual(a <= b, (1, 2))
        self.assertEqual(a > b, (1, 2))
        self.assertEqual(a >= b, (1, 2))

    def test_BitwiseInfix(self):
        a = FakeBitwiseInfix(1)
        b = 2
        self.assertEqual(a >> b, (1, 2))
        self.assertEqual(b >> a, (2, 1))
        self.assertEqual(a << b, (1, 2))
        self.assertEqual(b << a, (2, 1))

    def test_ItemInfix(self):
        a = FakeItemInfix(1)
        self.assertEqual(a['foo'], 1)

        a = FakeItemInfix(1)
        a['foo'] = 'bar'
        self.assertEqual(a.data, 'bar')

        a = FakeItemInfix(1)
        self.assertEqual(a['missing'], 'missing')

        a = FakeItemInfix(1)
        del a['foo']
        self.assertIs(a.data, None)

    def test_UnaryInfix(self):
        a = FakeUnaryInfix(1)
        self.assertEqual(~a, 'not 1')
        self.assertEqual(-a, 'not 1')
        self.assertEqual(+a, 'not 1')

    def test_EqualityInfix(self):
        a = FakeEqualityInfix(1)
        b = 2
        self.assertEqual(a == b, (1, 2))
        self.assertEqual(a != b, (1, 2))

    def test_AssignmentInfix(self):
        b = 2

        a = FakeAssignmentInfix(1)
        a += b
        self.assertEqual(a, (1, 2))

        a = FakeAssignmentInfix(1)
        a -= b
        self.assertEqual(a, (1, 2))

        a = FakeAssignmentInfix(1)
        a *= b
        self.assertEqual(a, (1, 2))

        a = FakeAssignmentInfix(1)
        a /= b
        self.assertEqual(a, (1, 2))

        a = FakeAssignmentInfix(1)
        a %= b
        self.assertEqual(a, (1, 2))

        a = FakeAssignmentInfix(1)
        a //= b
        self.assertEqual(a, (1, 2))

        a = FakeAssignmentInfix(1)
        a **= b
        self.assertEqual(a, (1, 2))

        a = FakeAssignmentInfix(1)
        a @= b
        self.assertEqual(a, (1, 2))

        a = FakeAssignmentInfix(1)
        a &= b
        self.assertEqual(a, (1, 2))

        a = FakeAssignmentInfix(1)
        a |= b
        self.assertEqual(a, (1, 2))

        a = FakeAssignmentInfix(1)
        a ^= b
        self.assertEqual(a, (1, 2))

        a = FakeAssignmentInfix(1)
        a >>= b
        self.assertEqual(a, (1, 2))

        a = FakeAssignmentInfix(1)
        a <<= b
        self.assertEqual(a, (1, 2))

    def test_MiscInfix(self):
        a = FakeMiscInfix(1)

        del a.foo
        self.assertIs(a.data, None)

        a = FakeMiscInfix(1)
        self.assertTrue('foo' in a)
