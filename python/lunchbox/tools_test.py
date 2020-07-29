import os
import unittest

from lunchbox import tools
# ------------------------------------------------------------------------------


@tools.api_function
def foobar_func(foo='<required>', bar='bar'):
    return foo + bar


class ToolsTests(unittest.TestCase):
    def test_relative_path(self):
        result = tools.relative_path(__file__, '../../resources/foo.txt')
        self.assertTrue(os.path.exists(result))

    def test_is_standard_module(self):
        self.assertTrue(tools.is_standard_module('re'))
        self.assertTrue(tools.is_standard_module('math'))
        self.assertFalse(tools.is_standard_module('cv2'))
        self.assertFalse(tools.is_standard_module('pandas'))

    def test_get_function_signature(self):
        def func(a, b, foo='bar', boo='baz'):
            pass
        result = tools.get_function_signature(func)
        expected = dict(
            args=['a', 'b'],
            kwargs=dict(foo='bar', boo='baz')
        )
        self.assertEqual(result, expected)

        def func(a, b):
            pass
        result = tools.get_function_signature(func)
        expected = dict(
            args=['a', 'b'],
            kwargs={},
        )
        self.assertEqual(result, expected)

        def func(foo='bar', boo='baz'):
            pass
        result = tools.get_function_signature(func)
        expected = dict(
            args=[],
            kwargs=dict(foo='bar', boo='baz')
        )
        self.assertEqual(result, expected)

        def func():
            pass
        result = tools.get_function_signature(func)
        expected = dict(
            args=[],
            kwargs={},
        )
        self.assertEqual(result, expected)

    def test_api_function(self):
        result = foobar_func(foo='taco', bar='cat')
        self.assertEqual(result, 'tacocat')

        result = foobar_func(foo='foo')
        self.assertEqual(result, 'foobar')

    def test_api_function_non_keyword(self):
        @tools.api_function
        def foobar_func(foo, bar='bar'):
            return foo + bar
        expected = 'Function may only have keyword arguments. '
        expected += r"Found non-keyword arguments: \['foo'\]."
        with self.assertRaisesRegex(TypeError, expected):
            foobar_func('foo', bar='bar')

    def test_api_function_no_keywords(self):
        @tools.api_function
        def foobar_func():
            return 'foobar'
        result = foobar_func()
        self.assertEqual(result, 'foobar')

        expected = r'foobar_func\(\) takes 0 positional arguments but 1 was given'
        with self.assertRaisesRegex(TypeError, expected):
            foobar_func('foo')

        expected = r"foobar_func\(\) got an unexpected keyword argument 'foo'"
        with self.assertRaisesRegex(TypeError, expected):
            foobar_func(foo='foo')

    def test_api_function_bad_keyword(self):
        expected = r"foobar_func\(\) got an unexpected keyword argument 'pizza'"
        with self.assertRaisesRegex(TypeError, expected):
            foobar_func(foo='foo', pizza='on a bagel')

    def test_api_function_required(self):
        expected = 'Missing required keyword argument: foo.'
        with self.assertRaisesRegex(ValueError, expected):
            foobar_func(bar='pumpkin')

    def test_try_(self):
        result = tools.try_(lambda x: int(x), 1.0, return_item='item')
        self.assertEqual(result, 1)

        result = tools.try_(lambda x: int(x), 'foo', return_item='bar')
        self.assertEqual(result, 'bar')

        result = tools.try_(lambda x: int(x), 'foo')
        self.assertEqual(result, 'foo')

        result = tools.try_(lambda x: int(x), 'foo', return_item='error')
        self.assertIsInstance(result, ValueError)

    def test_get_ordered_unique(self):
        x = [0, 0, 0, 1, 1, 2, 3, 4, 5, 5, 5]
        result = tools.get_ordered_unique(x)
        expected = [0, 1, 2, 3, 4, 5]
        self.assertEqual(result, expected)
