import unittest

from lunchbox.singleton import Singleton
# ------------------------------------------------------------------------------


class SingletonTests(unittest.TestCase):
    def test_singleton(self):
        class Foo(Singleton):
            def __init__(self):
                self.foo = 'pizza'

        a = Foo()
        b = Foo()
        a.foo = 'bar'
        self.assertIs(a, b)
        self.assertEqual(a.foo, 'bar')
        self.assertEqual(b.foo, 'bar')
