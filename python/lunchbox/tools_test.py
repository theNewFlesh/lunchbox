import multiprocessing
import os
import time
import unittest
from lunchbox.enforce import EnforceError

import lunchbox.tools as lbt
# ------------------------------------------------------------------------------


@lbt.api_function
def foobar_func(foo='<required>', bar='bar'):
    return foo + bar


def _log_runtime_func(a, b, c):
    time.sleep(0.01)
    return sum([a, b, c])


def _runtime_func(a, b, c):
    @lbt.runtime
    def func(a, b, c):
        time.sleep(0.01)
        return sum([a, b, c])
    return func(a, b, c)


class ToolsTests(unittest.TestCase):

    def test_to_snakecase(self):
        x = 'camelCase.SCREAMING__SNAKE_CASE-kebab-case..dot.case  space '
        x += 'case-fat-face.ratRace'
        result = lbt.to_snakecase(x)
        expected = 'camel_case_screaming_snake_case_kebab_case_dot_case_space'
        expected += '_case_fat_face_rat_race'
        self.assertEqual(result, expected)

        items = [
            'fooBar',
            'foo_bar',
            'foo__bar',
            'foo.bar',
            'foo..bar',
            'foo-bar',
            'foo--bar',
            'foo bar',
            'foo  bar',
            '_foo_bar_',
            '_foo__bar_',
            '.foo.bar.',
            '.foo..bar.',
            '-foo-bar-',
            '-foo--bar-',
            ' foo bar ',
            ' foo  bar ',
        ]
        for item in items:
            result = lbt.to_snakecase(item)
            self.assertEqual(result, 'foo_bar')

    def test_relative_path(self):
        result = lbt.relative_path(__file__, '../../resources/foo.txt')
        self.assertTrue(os.path.exists(result))

    def test_is_standard_module(self):
        self.assertTrue(lbt.is_standard_module('re'))
        self.assertTrue(lbt.is_standard_module('math'))
        self.assertFalse(lbt.is_standard_module('cv2'))
        self.assertFalse(lbt.is_standard_module('pandas'))

    def test_get_function_signature(self):
        def func(a, b, foo='bar', boo='baz'):
            pass
        result = lbt.get_function_signature(func)
        expected = dict(
            args=['a', 'b'],
            kwargs=dict(foo='bar', boo='baz')
        )
        self.assertEqual(result, expected)

        def func(a, b):
            pass
        result = lbt.get_function_signature(func)
        expected = dict(
            args=['a', 'b'],
            kwargs={},
        )
        self.assertEqual(result, expected)

        def func(foo='bar', boo='baz'):
            pass
        result = lbt.get_function_signature(func)
        expected = dict(
            args=[],
            kwargs=dict(foo='bar', boo='baz')
        )
        self.assertEqual(result, expected)

        def func():
            pass
        result = lbt.get_function_signature(func)
        expected = dict(
            args=[],
            kwargs={},
        )
        self.assertEqual(result, expected)

    def test_truncate_list(self):
        items = [1, 2, 3, 4, 5]

        # default size
        result = lbt.truncate_list(items)
        self.assertEqual(result, [1, '...', 5])

        # len(items) < size
        result = lbt.truncate_list(items, size=100)
        self.assertEqual(result, items)

        # size 0
        result = lbt.truncate_list(items, size=0)
        self.assertEqual(result, [])

        # size 1
        result = lbt.truncate_list(items, size=1)
        self.assertEqual(result, [1])

        # size 2
        result = lbt.truncate_list(items, size=2)
        self.assertEqual(result, [1, 5])

        # size 3
        result = lbt.truncate_list(items, size=3)
        self.assertEqual(result, [1, '...', 5])

        # size 4
        result = lbt.truncate_list(items, size=4)
        self.assertEqual(result, [1, 2, '...', 5])

        # size 5
        result = lbt.truncate_list(items, size=5)
        self.assertEqual(result, [1, 2, 3, 4, 5])

    def test_truncate_list_errors(self):
        expected = 'Items must be a list.'
        with self.assertRaisesRegexp(EnforceError, expected):
            lbt.truncate_list('foo')

        items = [1, 2, 3, 4, 5]
        expected = 'Size must be an integer greater than -1. Given value: foo.'
        with self.assertRaisesRegexp(EnforceError, expected):
            lbt.truncate_list(items, size='foo')

        expected = 'Size must be an integer greater than -1. Given value: 9.2.'
        with self.assertRaisesRegexp(EnforceError, expected):
            lbt.truncate_list(items, size=9.2)

        expected = 'Size must be an integer greater than -1. Given value: -1.'
        with self.assertRaisesRegexp(EnforceError, expected):
            lbt.truncate_list(items, size=-1)

    # LOGGING-------------------------------------------------------------------
    def test_log_runtime(self):
        def func(a, b, c, x=0, y=1, z=2):
            time.sleep(0.01)
            return sum([a, b, c, x, y, z])

        result = lbt.log_runtime(func, 1, 2, 3, x=4, y=5, z=6)
        self.assertEqual(result, 21)

        result = lbt.log_runtime(func, 1, 2, 3, x=4, y=5, z=6, _testing=True)
        expected = '''func
         Runtime: 0.01 seconds
            Args: (1, 2, 3)
          Kwargs: {'x': 4, 'y': 5, 'z': 6}'''
        self.assertEqual(result, expected)

        result = lbt.log_runtime(
            func, 1, 2, 3, x=4, y=5, z=6, message_='foo', _testing=True
        )
        expected = 'foo\n         Runtime: 0.01 seconds'
        self.assertEqual(result, expected)

    def test_log_runtime_multiprocessing(self):
        args = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        with multiprocessing.Pool(processes=2) as pool:
            result = pool.starmap(_log_runtime_func, args)
        self.assertEqual(sum(result), 45)

    def test_runtime(self):
        result = _runtime_func(1, 2, 3)
        self.assertEqual(result, 6)

    def test_runtime_multiprocessing(self):
        args = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        with multiprocessing.Pool(processes=2) as pool:
            result = pool.starmap(_runtime_func, args)
        self.assertEqual(sum(result), 45)

    # API-----------------------------------------------------------------------
    def test_api_function(self):
        result = foobar_func(foo='taco', bar='cat')
        self.assertEqual(result, 'tacocat')

        result = foobar_func(foo='foo')
        self.assertEqual(result, 'foobar')

    def test_api_function_non_keyword(self):
        @lbt.api_function
        def foobar_func(foo, bar='bar'):
            return foo + bar
        expected = 'Function may only have keyword arguments. '
        expected += r"Found non-keyword arguments: \['foo'\]."
        with self.assertRaisesRegex(TypeError, expected):
            foobar_func('foo', bar='bar')

    def test_api_function_no_keywords(self):
        @lbt.api_function
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
        result = lbt.try_(lambda x: int(x), 1.0, return_item='item')
        self.assertEqual(result, 1)

        result = lbt.try_(lambda x: int(x), 'foo', return_item='bar')
        self.assertEqual(result, 'bar')

        result = lbt.try_(lambda x: int(x), 'foo')
        self.assertEqual(result, 'foo')

        result = lbt.try_(lambda x: int(x), 'foo', return_item='error')
        self.assertIsInstance(result, ValueError)

    def test_get_ordered_unique(self):
        x = [0, 0, 0, 1, 1, 2, 3, 4, 5, 5, 5]
        result = lbt.get_ordered_unique(x)
        expected = [0, 1, 2, 3, 4, 5]
        self.assertEqual(result, expected)
