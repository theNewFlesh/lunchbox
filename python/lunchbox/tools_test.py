from pathlib import Path
from tempfile import TemporaryDirectory
import logging
import multiprocessing
import os
import time
import unittest

from lunchbox.enforce import EnforceError
from lunchbox.stopwatch import StopWatch
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


class ExampleClass:
    def func_public(self):
        pass

    def _func_semiprivate(self):
        pass

    def __func_private(self):
        pass

    def very_long_func_public(self):
        pass

    def _very_long_func_semiprivate(self):
        pass

    def __very_long_func_private(self):
        pass

    def _Func_semiprivate(self):
        pass


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

    def test_dir_table_header(self):
        result = lbt._dir_table(
            ExampleClass, public=True, semiprivate=True, private=True,
        ).split('\n')[0]
        expected = '^NAME +TYPE +VALUE$'
        self.assertRegex(result, expected)

    def test_dir_table_public(self):
        result = lbt._dir_table(
            ExampleClass, public=True, semiprivate=False, private=False,
        )
        self.assertIn('func_public', result)
        self.assertIn('very_long_func_public', result)
        self.assertNotIn('_Func_semiprivate', result)
        self.assertNotIn('_func_semiprivate', result)
        self.assertNotIn('_very_long_func_semiprivate', result)
        self.assertNotIn('__func_private', result)
        self.assertNotIn('__very_long_func_private', result)

    def test_dir_table_semiprivate(self):
        result = lbt._dir_table(
            ExampleClass, public=False, semiprivate=True, private=False,
        )
        self.assertNotIn('func_public', result)
        self.assertNotIn('very_long_func_public', result)
        self.assertIn('_Func_semiprivate', result)
        self.assertIn('_func_semiprivate', result)
        self.assertIn('_very_long_func_semiprivate', result)
        self.assertNotIn('__func_private', result)
        self.assertNotIn('__very_long_func_private', result)

    def test_dir_table_private(self):
        result = lbt._dir_table(
            ExampleClass, public=False, semiprivate=False, private=True,
        )
        self.assertNotIn('func_public', result)
        self.assertNotIn('very_long_func_public', result)
        self.assertNotIn('_Func_semiprivate', result)
        self.assertNotIn('_func_semiprivate', result)
        self.assertNotIn('_very_long_func_semiprivate', result)
        self.assertIn('__func_private', result)
        self.assertIn('__very_long_func_private', result)

    def test_dir_table_max_width(self):
        result = lbt._dir_table(ExampleClass, max_width=52).split('\n')
        for line in result:
            self.assertLessEqual(len(line), 52)

        result = lbt._dir_table(
            ExampleClass,
            public=True, semiprivate=True, private=True, max_width=52
        ).split('\n')
        for line in result:
            self.assertLessEqual(len(line), 52)

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
        with self.assertRaisesRegex(EnforceError, expected):
            lbt.truncate_list('foo')

        items = [1, 2, 3, 4, 5]
        expected = 'Size must be an integer greater than -1. Given value: foo.'
        with self.assertRaisesRegex(EnforceError, expected):
            lbt.truncate_list(items, size='foo')

        expected = 'Size must be an integer greater than -1. Given value: 9.2.'
        with self.assertRaisesRegex(EnforceError, expected):
            lbt.truncate_list(items, size=9.2)

        expected = 'Size must be an integer greater than -1. Given value: -1.'
        with self.assertRaisesRegex(EnforceError, expected):
            lbt.truncate_list(items, size=-1)

    def test_truncate_blob_lists(self):
        items = [1, 2, 3, 4, 5]
        d_items = {'list': items}
        blob = {
            'str': '',
            'list': items,
            'dict': {
                'list': items,
                'str': ''
            },
            'nested-list': [items, [items], [[items]], [[[items]]]],
            'list-dict': [d_items, d_items, d_items, d_items],
            'complex': {
                'list': [
                    [d_items, items, '', items, '']
                ]
            }
        }

        # size 3
        e_items = [1, '...', 5]
        d_e_items = {'list': e_items}
        expected = {
            'str': '',
            'list': e_items,
            'dict': {
                'list': e_items,
                'str': ''
            },
            'nested-list': [e_items, '...', [[[e_items]]]],
            'list-dict': [d_e_items, '...', d_e_items],
            'complex': {
                'list': [
                    [d_e_items, '...', '']
                ]
            }
        }
        result = lbt.truncate_blob_lists(blob, size=3)
        self.assertEqual(result, expected)

        # size 2
        e_items = [1, 5]
        d_e_items = {'list': e_items}
        expected = {
            'str': '',
            'list': e_items,
            'dict': {
                'list': e_items,
                'str': ''
            },
            'nested-list': [e_items, [[[e_items]]]],
            'list-dict': [d_e_items, d_e_items],
            'complex': {
                'list': [
                    [d_e_items, '']
                ]
            }
        }
        result = lbt.truncate_blob_lists(blob, size=2)
        self.assertEqual(result, expected)

    def test_truncate_blob_lists_errors(self):
        expected = 'Blob must be a dict.'
        with self.assertRaisesRegex(EnforceError, expected):
            lbt.truncate_blob_lists('foo')

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

    def test_log_runtime_log_level(self):
        def func():
            time.sleep(0.001)

        with self.assertLogs('lunchbox.tools', level=logging.WARNING):
            lbt.log_runtime(func, log_level='warning')

        with self.assertLogs('lunchbox.tools', level=logging.ERROR):
            lbt.log_runtime(func, log_level='error')

    def test_log_runtime_multiprocessing(self):
        args = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        # TODO: solve deprecation warning here
        with multiprocessing.Pool(processes=2) as pool:
            result = pool.starmap(_log_runtime_func, args)
        self.assertEqual(sum(result), 45)

    def test_runtime(self):
        result = _runtime_func(1, 2, 3)
        self.assertEqual(result, 6)

    def test_runtime_multiprocessing(self):
        args = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        # TODO: solve deprecation warning here
        with multiprocessing.Pool(processes=2) as pool:
            result = pool.starmap(_runtime_func, args)
        self.assertEqual(sum(result), 45)

    # HTTP-REQUESTS-------------------------------------------------------------
    def test_post_to_slack(self):
        result = lbt.post_to_slack(
            'https://hooks.slack.com/services/foo/bar', 'channel', 'message'
        ).status
        self.assertEqual(result, 200)

    def test_post_to_slack_errors(self):
        url = 'https://hooks.slack.com/services/foo/bar',
        with self.assertRaises(EnforceError):
            lbt.post_to_slack(99, 'channel', 'message')

        with self.assertRaises(EnforceError):
            lbt.post_to_slack(url, 99, 'message')

        with self.assertRaises(EnforceError):
            lbt.post_to_slack(url, 'channel', 99)

        expected = 'URL must begin with https://hooks.slack.com/services/. '
        expected += 'Given URL: http://foo.com/bar'
        with self.assertRaisesRegex(EnforceError, expected):
            lbt.post_to_slack('http://foo.com/bar', 'channel', 'message')

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

    def test_log_level_to_int(self):
        levels = [
            'critical', 'debug', 'error', 'fatal', 'info', 'warn', 'warning'
        ]
        for level in levels:
            result = lbt.log_level_to_int(level)
            expected = getattr(logging, level.upper())
            self.assertEqual(result, expected)

        result = lbt.log_level_to_int(50)
        self.assertEqual(result, 50)

    def test_log_level_to_int_error(self):
        expected = r'Log level must be an integer or string\. '
        expected += r'Given value: {}\. '
        expected += r'Legal values: \[critical: 50, debug: 10, error: 40, '
        expected += r'fatal: 50, info: 20, warn: 30, warning: 30\]\.'

        # level int
        with self.assertRaisesRegex(EnforceError, expected.format(99)):
            lbt.log_level_to_int(99)

        # level str
        with self.assertRaisesRegex(EnforceError, expected.format('foobar')):
            lbt.log_level_to_int('foobar')

        # level float
        with self.assertRaisesRegex(EnforceError, expected.format(1.0)):
            lbt.log_level_to_int(1.0)


    def test_regex_match(self):
        string = lbt.RegexMatch('foo')
        match string:
            case '.*foo.*':
                pass
            case _:
                raise AssertionError

    def create_files(self, root):
        filepaths = [
            'a/1.foo',
            'a/b/2.json',
            'a/b/3.txt',
            'a/b/c/4.json',
            'a/b/c/5.txt'
        ]
        filepaths = [Path(root, x) for x in filepaths]
        for filepath in filepaths:
            os.makedirs(filepath.parent, exist_ok=True)
            with open(filepath, 'w') as f:
                f.write('')
        return filepaths

    def test_format_block(self):
        text = '''
            foo
                bar
                    baz
        '''
        expected = '''
    foo
        bar
            baz
'''[1:-1]
        result = lbt.format_block(text, dedent=12, indent=4)
        self.assertEqual(result, expected)

        text = '''    
    foo
        bar
    '''
        expected = '''
foo
    bar
'''[1:-1]
        result = lbt.format_block(text, dedent=4, indent=0)
        self.assertEqual(result, expected)

    def test_format_block_collapse(self):
        items = [
            '', ' ', '\t', ' \t\n',
            '''
            '''
        ]
        for item in items:
            result = lbt.format_block(item, indent=5, collapse=True)
            self.assertEqual(result, '')

    def test_autoformat_block(self):
        text = '''
        foo
            bar
        '''
        result = lbt.autoformat_block(text)
        self.assertEqual(result, 'foo\n    bar')

        text = '''
        foo
        bar
        '''
        result = lbt.autoformat_block(text)
        self.assertEqual(result, 'foo\nbar')

        text = '''
foo
bar
'''
        result = lbt.autoformat_block(text)
        self.assertEqual(result, 'foo\nbar')

        text = '''
  foo
    bar
'''
        result = lbt.autoformat_block(text)
        self.assertEqual(result, 'foo\n  bar')

        text = lbt.format_block('''
            users = [
                {'name': 'john', 'role': 'admin'},
                {'name': 'bill', 'role': 'admin'},
                {'name': 'jacob', 'role': 'user'},
            ]
            result = filter_admin_users(users)
            assert result == users[:2]
        ''', dedent=8)
        expected = lbt.format_block('''
            users = [
                {'name': 'john', 'role': 'admin'},
                {'name': 'bill', 'role': 'admin'},
                {'name': 'jacob', 'role': 'user'},
            ]
            result = filter_admin_users(users)
            assert result == users[:2]
        ''', dedent=12)
        result = lbt.autoformat_block(text)
        self.assertEqual(result, expected)

    def test_autoformat_block_no_indent(self):
        result = lbt.autoformat_block('')
        self.assertEqual(result, '')

    def test_traverse_directory(self):
        with TemporaryDirectory() as root:
            expected = sorted(self.create_files(root))
            result = sorted(list(lbt.traverse_directory(root)))
            self.assertEqual(result, expected)

    def test_traverse_directory_directory(self):
        with TemporaryDirectory() as root:
            self.create_files(root)
            expected = [
                Path(root, 'a'),
                Path(root, 'a/b'),
                Path(root, 'a/b/c'),
            ]
            result = sorted(list(lbt.traverse_directory(root, entry_type='directory')))
            self.assertEqual(result, expected)

    def test_traverse_directory_error(self):
        expected = '/foo/bar is not a directory or does not exist.'
        with self.assertRaisesRegex(FileNotFoundError, expected):
            next(lbt.traverse_directory('/foo/bar'))

        expected = '/foo.bar is not a directory or does not exist.'
        with self.assertRaisesRegex(FileNotFoundError, expected):
            next(lbt.traverse_directory('/foo.bar'))

        expected = 'Illegal entry type: foobar. Legal entry types: '
        expected += r"\['file', 'directory'\]\."
        with self.assertRaisesRegex(EnforceError, expected):
            next(lbt.traverse_directory('/tmp', entry_type='foobar'))

    def test_traverse_directory_include(self):
        with TemporaryDirectory() as root:
            regex = r'\.txt'

            self.create_files(root)
            expected = [
                Path(root, 'a/b/3.txt'),
                Path(root, 'a/b/c/5.txt'),
            ]

            result = lbt.traverse_directory(root, include_regex=regex)
            result = sorted(list(result))
            self.assertEqual(result, expected)

    def test_traverse_directory_exclude(self):
        with TemporaryDirectory() as root:
            regex = r'\.txt'

            self.create_files(root)
            expected = [
                Path(root, 'a/1.foo'),
                Path(root, 'a/b/2.json'),
                Path(root, 'a/b/c/4.json'),
            ]

            result = lbt.traverse_directory(root, exclude_regex=regex)
            result = sorted(list(result))
            self.assertEqual(result, expected)

    def test_traverse_directory_include_exclude(self):
        with TemporaryDirectory() as root:
            i_regex = r'/a/b'
            e_regex = r'\.json'

            self.create_files(root)
            expected = [
                Path(root, 'a/b/3.txt'),
                Path(root, 'a/b/c/5.txt'),
            ]

            result = lbt.traverse_directory(
                root,
                include_regex=i_regex,
                exclude_regex=e_regex
            )
            result = sorted(list(result))
            self.assertEqual(result, expected)

    def test_str_to_bool(self):
        assert lbt.str_to_bool('true') is True
        assert lbt.str_to_bool('True') is True
        assert lbt.str_to_bool('TRUE') is True
        assert lbt.str_to_bool('TrUe') is True

        assert lbt.str_to_bool('false') is False
        assert lbt.str_to_bool('False') is False
        assert lbt.str_to_bool('FALSE') is False
        assert lbt.str_to_bool('any-string') is False


class LogRuntimeTest(unittest.TestCase):
    def test_init(self):
        result = lbt.LogRuntime(
            message='message',
            name='test',
            level='debug',
            suppress=True,
        )
        self.assertEqual(result._message, 'message')
        self.assertIsInstance(result._stopwatch, lbt.StopWatch)
        self.assertIsInstance(result._logger, logging.Logger)
        self.assertEqual(result._level, logging.DEBUG)
        self.assertEqual(result._suppress, True)

    def test_init_errors(self):
        # message
        with self.assertRaises(EnforceError):
            lbt.LogRuntime(message=199)

        # name
        with self.assertRaises(EnforceError):
            lbt.LogRuntime(name=99)

        # suppress
        with self.assertRaises(EnforceError):
            lbt.LogRuntime(suppress=99)

    def test_with(self):
        msg = 'Foo the bars'
        with lbt.LogRuntime(msg, name='foobar', level='debug'):
            time.sleep(0.001)

        # suppress
        expected = r'Foo the bars - Runtime: 0:00:00\..* \(.* seconds?\)'
        with lbt.LogRuntime(msg, suppress=True) as log:
            time.sleep(0.001)
        self.assertRegex(log.message, expected)

        # suppress no message
        expected = r'Runtime: 0:00:00\..* \(.* seconds?\)'
        with lbt.LogRuntime(suppress=True) as log:
            time.sleep(0.001)
        self.assertRegex(log.message, expected)

    def test_default_message_func(self):
        stopwatch = StopWatch()
        stopwatch.start()
        time.sleep(0.001)
        stopwatch.stop()
        expected = r'foobar - Runtime: 0:00:00\..* \(.* seconds?\)'
        result = lbt.LogRuntime._default_message_func('foobar', stopwatch)
        self.assertRegex(result, expected)

    def test_default_message_func_errors(self):
        stopwatch = StopWatch()
        stopwatch.start()
        stopwatch.stop()
        with self.assertRaises(EnforceError):
            lbt.LogRuntime._default_message_func(10, stopwatch)

        with self.assertRaises(EnforceError):
            lbt.LogRuntime._default_message_func('msg', None)

    def test_callback(self):
        result = []

        def func(x):
            result.append(x)

        with lbt.LogRuntime(suppress=True, callback=func) as log:
            time.sleep(0.001)
        self.assertEqual(result[0], log.message)

    def test_message_func(self):
        def func(msg, stopwatch):
            return 'foobar - ' + str(stopwatch.delta.seconds)

        with lbt.LogRuntime(suppress=True, message_func=func) as log:
            time.sleep(0.001)
        expected = r'foobar - \d+$'
        self.assertRegex(log.message, expected)

    def test_message_func_with_callback(self):
        result = []

        def callback(x):
            result.append(x)

        def msg_func(msg, stopwatch):
            return 'foobar - ' + str(stopwatch.delta.seconds)

        with lbt.LogRuntime(
            suppress=True, message_func=msg_func, callback=callback
        ):
            time.sleep(0.001)
        expected = r'foobar - \d+$'
        self.assertRegex(result[0], expected)
