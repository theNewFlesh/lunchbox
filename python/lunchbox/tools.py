from typing import Any, Callable, Dict, List, Optional, Union

from itertools import dropwhile, takewhile
from pathlib import Path
from pprint import pformat
import inspect
import logging
import os
import re

import wrapt

from lunchbox.enforce import Enforce
from lunchbox.stopwatch import StopWatch

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING').upper()
logging.basicConfig(level=LOG_LEVEL)
LOGGER = logging.getLogger(__name__)
# ------------------------------------------------------------------------------


'''
A library of miscellaneous tools.
'''


def to_snakecase(string):
    # type: (str) -> str
    '''
    Converts a given string to snake_case.

    Args:
        string (str): String to be converted.

    Returns:
        str: snake_case string.
    '''
    output = re.sub('([A-Z]+)', r'_\1', string)
    output = re.sub('-', '_', output)
    output = re.sub(r'\.', '_', output)
    output = re.sub(' ', '_', output)
    output = re.sub('_+', '_', output)
    output = re.sub('^_|_$', '', output)
    output = output.lower()
    return output


def try_(function, item, return_item='item'):
    # type: (Callable[[Any], Any], Any, Any) -> Any
    '''
    Call given function on given item, catch any exceptions and return given
    return item.

    Args:
        function (function): Function of signature lambda x: x.
        item (object): Item used to call function.
        return_item (object, optional): Item to be returned. Default: "item".

    Returns:
        object: Original item if return_item is "item".
        Exception: If return_item is "error".
        object: Object return by function call if return_item is not "item" or
            "error".
    '''
    try:
        return function(item)
    except Exception as error:
        if return_item == 'item':
            return item
        elif return_item == 'error':
            return error
        return return_item


def get_ordered_unique(items):
    # type: (List) -> List
    '''
    Generates a unique list of items in same order they were received in.

    Args:
        items (list): List of items.

    Returns:
        list: Unique ordered list.
    '''
    output = []
    temp = set()
    for item in items:
        if item not in temp:
            output.append(item)
            temp.add(item)
    return output


def relative_path(module, path):
    # type: (Union[str, Path], Union[str, Path]) -> Path
    '''
    Resolve path given current module's file path and given suffix.

    Args:
        module (str or Path): Always __file__ of current module.
        path (str or Path): Path relative to __file__.

    Returns:
        Path: Resolved Path object.
    '''
    module_root = Path(module).parent
    path_ = Path(path).parts  # type: Any
    path_ = list(dropwhile(lambda x: x == ".", path_))
    up = len(list(takewhile(lambda x: x == "..", path_)))
    path_ = Path(*path_[up:])
    root = list(module_root.parents)[up - 1]
    output = Path(root, path_).absolute()

    LOGGER.debug(
        f'relative_path called with: {module} and {path_}. Returned: {output}')
    return output


def truncate_list(items, size=3):
    # type (list, int) -> list
    '''
    Truncates a given list to a given size, replaces the middle contents with
    "...".

    Args:
        items (list): List of objects.
        size (int, optional): Size of output list.

    Raises:
        EnforceError: If item is not a list.
        EnforceError: If size is not an integer greater than -1.

    Returns:
        list: List of given size.
    '''
    Enforce(items, 'instance of', list, message='Items must be a list.')
    msg = 'Size must be an integer greater than -1. Given value: {a}.'
    Enforce(size, 'instance of', int, message=msg)
    Enforce(size, '>', -1, message=msg)
    # --------------------------------------------------------------------------

    if len(items) <= size:
        return items
    if size == 0:
        return []
    if size == 1:
        return items[:1]
    if size == 2:
        return [items[0], items[-1]]

    output = items[:size - 2]
    output.append('...')
    output.append(items[-1])
    return output


def truncate_blob_lists(blob, size=3):
    # type: (dict, int) -> dict
    '''
    Truncates lists inside given JSON blob to a given size.

    Args:
        blob (dict): Blob to be truncated.
        size (int, optional): Size of lists. Default 3.

    Raises:
        EnforceError: If blob is not a dict.

    Returns:
        dict: Truncated blob.
    '''
    Enforce(blob, 'instance of', dict, message='Blob must be a dict.')
    # --------------------------------------------------------------------------

    def recurse_list(items, size):
        output = []
        for item in truncate_list(items, size=size):
            if isinstance(item, dict):
                item = recurse(item)
            elif isinstance(item, list):
                item = recurse_list(item, size)
            output.append(item)
        return output

    def recurse(item):
        output = {}
        for k, v in item.items():
            if isinstance(v, dict):
                output[k] = recurse(v)
            elif isinstance(v, list):
                output[k] = recurse_list(v, size)
            else:
                output[k] = v
        return output
    return recurse(blob)


# LOGGING-----------------------------------------------------------------------
def log_runtime(function, *args, message_=None, _testing=False, **kwargs):
    # type (Callable, ..., Optional[str], bool, ...) -> Any
    r'''
    Logs the duration of given function called with given arguments.

    Args:
        function (function): Function to be called.
        \*args (object, optional): Arguments.
        message_ (str, optional): Message to be returned. Default: None.
        _testing (bool, optional): Returns message if True. Default: False.
        \*\*kwargs (object, optional): Keyword arguments.

    Returns:
        object: function(*args, **kwargs).
    '''
    # this may silently break file writes in multiprocessing
    stopwatch = StopWatch()
    stopwatch.start()
    output = function(*args, **kwargs)
    stopwatch.stop()

    if message_ is not None:
        message_ += f'\n         Runtime: {stopwatch.human_readable_delta}'
    else:
        message_ = f'''{function.__name__}
         Runtime: {stopwatch.human_readable_delta}
            Args: {pformat(args)}
          Kwargs: {pformat(kwargs)}'''

    if _testing:
        return message_

    LOGGER.info(message_)
    return output


@wrapt.decorator
def runtime(wrapped, instance, args, kwargs):
    # type: (Callable, Any, Any, Any) -> Any
    r'''
    Decorator for logging the duration of given function called with given
    arguments.

    Args:
        wrapped (function): Function to be called.
        instance (object): Needed by wrapt.
        \*args (object, optional): Arguments.
        \*\*kwargs (object, optional): Keyword arguments.

    Returns:
        function: Wrapped function.
    '''
    return log_runtime(wrapped, *args, **kwargs)


# API---------------------------------------------------------------------------
def get_function_signature(function):
    # type: (Callable) -> Dict
    '''
    Inspect a given function and return its arguments as a list and its keyword
    arguments as a dict.

    Args:
        function (function): Function to be inspected.

    Returns:
        dict: args and kwargs.
    '''
    spec = inspect.getfullargspec(function)
    args = list(spec.args)
    kwargs = {}  # type: Any
    if spec.defaults is not None:
        args = args[:-len(spec.defaults)]
        kwargs = list(spec.args)[-len(spec.defaults):]
        kwargs = dict(zip(kwargs, spec.defaults))
    return dict(args=args, kwargs=kwargs)


def api_function(wrapped=None, **kwargs):
    # type: (Optional[Callable], Any) -> Callable
    '''
    A decorator that enforces keyword argument only function signatures and
    required keyword argument values when called.

    Args:
        wrapped (function): For dev use. Default: None.
        \*\*kwargs (dict): Keyword arguments. # noqa: W605

    Raises:
        TypeError: If non-keyword argument found in functionn signature.
        ValueError: If keyword arg with value of '<required>' is found.

    Returns:
        api function.
    '''
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        sig = get_function_signature(wrapped)

        # ensure no arguments are present
        if len(sig['args']) > 0:
            msg = 'Function may only have keyword arguments. '
            msg += f"Found non-keyword arguments: {sig['args']}."
            raise TypeError(msg)

        # ensure all required kwarg values are present
        params = sig['kwargs']
        params.update(kwargs)
        for key, val in params.items():
            if val == '<required>':
                msg = f'Missing required keyword argument: {key}.'
                raise ValueError(msg)

        LOGGER.debug(f'{wrapped} called with {params}.')
        return wrapped(*args, **kwargs)
    return wrapper(wrapped)
# ------------------------------------------------------------------------------


def is_standard_module(name):
    # type: (str) -> bool
    '''
    Determines if given module name is a python builtin.

    Args:
        name (str): Python module name.

    Returns:
        bool: Whether string names a python module.
    '''
    return name in _PYTHON_STANDARD_MODULES


_PYTHON_STANDARD_MODULES = [
    '__future__',
    '__main__',
    '_dummy_thread',
    '_thread',
    'abc',
    'aifc',
    'argparse',
    'array',
    'ast',
    'asynchat',
    'asyncio',
    'asyncore',
    'atexit',
    'audioop',
    'base64',
    'bdb',
    'binascii',
    'binhex',
    'bisect',
    'builtins',
    'bz2',
    'calendar',
    'cgi',
    'cgitb',
    'chunk',
    'cmath',
    'cmd',
    'code',
    'codecs',
    'codeop',
    'collections',
    'collections.abc',
    'colorsys',
    'compileall',
    'concurrent',
    'concurrent.futures',
    'configparser',
    'contextlib',
    'contextvars',
    'copy',
    'copyreg',
    'cProfile',
    'crypt',
    'csv',
    'ctypes',
    'curses',
    'curses.ascii',
    'curses.panel',
    'curses.textpad',
    'dataclasses',
    'datetime',
    'dbm',
    'dbm.dumb',
    'dbm.gnu',
    'dbm.ndbm',
    'decimal',
    'difflib',
    'dis',
    'distutils',
    'distutils.archive_util',
    'distutils.bcppcompiler',
    'distutils.ccompiler',
    'distutils.cmd',
    'distutils.command',
    'distutils.command.bdist',
    'distutils.command.bdist_dumb',
    'distutils.command.bdist_msi',
    'distutils.command.bdist_packager',
    'distutils.command.bdist_rpm',
    'distutils.command.bdist_wininst',
    'distutils.command.build',
    'distutils.command.build_clib',
    'distutils.command.build_ext',
    'distutils.command.build_py',
    'distutils.command.build_scripts',
    'distutils.command.check',
    'distutils.command.clean',
    'distutils.command.config',
    'distutils.command.install',
    'distutils.command.install_data',
    'distutils.command.install_headers',
    'distutils.command.install_lib',
    'distutils.command.install_scripts',
    'distutils.command.register',
    'distutils.command.sdist',
    'distutils.core',
    'distutils.cygwinccompiler',
    'distutils.debug',
    'distutils.dep_util',
    'distutils.dir_util',
    'distutils.dist',
    'distutils.errors',
    'distutils.extension',
    'distutils.fancy_getopt',
    'distutils.file_util',
    'distutils.filelist',
    'distutils.log',
    'distutils.msvccompiler',
    'distutils.spawn',
    'distutils.sysconfig',
    'distutils.text_file',
    'distutils.unixccompiler',
    'distutils.util',
    'distutils.version',
    'doctest',
    'dummy_threading',
    'email',
    'email.charset',
    'email.contentmanager',
    'email.encoders',
    'email.errors',
    'email.generator',
    'email.header',
    'email.headerregistry',
    'email.iterators',
    'email.message',
    'email.mime',
    'email.parser',
    'email.policy',
    'email.utils',
    'encodings',
    'encodings.idna',
    'encodings.mbcs',
    'encodings.utf_8_sig',
    'ensurepip',
    'enum',
    'errno',
    'faulthandler',
    'fcntl',
    'filecmp',
    'fileinput',
    'fnmatch',
    'formatter',
    'fractions',
    'ftplib',
    'functools',
    'gc',
    'getopt',
    'getpass',
    'gettext',
    'glob',
    'grp',
    'gzip',
    'hashlib',
    'heapq',
    'hmac',
    'html',
    'html.entities',
    'html.parser',
    'http',
    'http.client',
    'http.cookiejar',
    'http.cookies',
    'http.server',
    'imaplib',
    'imghdr',
    'imp',
    'importlib',
    'importlib.abc',
    'importlib.machinery',
    'importlib.resources',
    'importlib.util',
    'inspect',
    'io',
    'ipaddress',
    'itertools',
    'json',
    'json.tool',
    'keyword',
    'lib2to3',
    'linecache',
    'locale',
    'logging',
    'logging.config',
    'logging.handlers',
    'lzma',
    'macpath',
    'mailbox',
    'mailcap',
    'marshal',
    'math',
    'mimetypes',
    'mmap',
    'modulefinder',
    'msilib',
    'msvcrt',
    'multiprocessing',
    'multiprocessing.connection',
    'multiprocessing.dummy',
    'multiprocessing.managers',
    'multiprocessing.pool',
    'multiprocessing.sharedctypes',
    'netrc',
    'nis',
    'nntplib',
    'numbers',
    'operator',
    'optparse',
    'os',
    'os.path',
    'ossaudiodev',
    'parser',
    'pathlib',
    'pdb',
    'pickle',
    'pickletools',
    'pipes',
    'pkgutil',
    'platform',
    'plistlib',
    'poplib',
    'posix',
    'pprint',
    'profile',
    'pstats',
    'pty',
    'pwd',
    'py_compile',
    'pyclbr',
    'pydoc',
    'queue',
    'quopri',
    'random',
    're',
    'readline',
    'reprlib',
    'resource',
    'rlcompleter',
    'runpy',
    'sched',
    'secrets',
    'select',
    'selectors',
    'shelve',
    'shlex',
    'shutil',
    'signal',
    'site',
    'smtpd',
    'smtplib',
    'sndhdr',
    'socket',
    'socketserver',
    'spwd',
    'sqlite3',
    'ssl',
    'stat',
    'statistics',
    'string',
    'stringprep',
    'struct',
    'subprocess',
    'sunau',
    'symbol',
    'symtable',
    'sys',
    'sysconfig',
    'syslog',
    'tabnanny',
    'tarfile',
    'telnetlib',
    'tempfile',
    'termios',
    'test',
    'test.support',
    'test.support.script_helper',
    'textwrap',
    'threading',
    'time',
    'timeit',
    'tkinter',
    'tkinter.scrolledtext',
    'tkinter.tix',
    'tkinter.ttk',
    'token',
    'tokenize',
    'trace',
    'traceback',
    'tracemalloc',
    'tty',
    'turtle',
    'turtledemo',
    'types',
    'typing',
    'unicodedata',
    'unittest',
    'unittest.mock',
    'urllib',
    'urllib.error',
    'urllib.parse',
    'urllib.request',
    'urllib.response',
    'urllib.robotparser',
    'uu',
    'uuid',
    'venv',
    'warnings',
    'wave',
    'weakref',
    'webbrowser',
    'winreg',
    'winsound',
    'wsgiref',
    'wsgiref.handlers',
    'wsgiref.headers',
    'wsgiref.simple_server',
    'wsgiref.util',
    'wsgiref.validate',
    'xdrlib',
    'xml',
    'xml.dom',
    'xml.dom.minidom',
    'xml.dom.pulldom',
    'xml.etree.ElementTree',
    'xml.parsers.expat',
    'xml.parsers.expat.errors',
    'xml.parsers.expat.model',
    'xml.sax',
    'xml.sax.handler',
    'xml.sax.saxutils',
    'xml.sax.xmlreader',
    'xmlrpc',
    'xmlrpc.client',
    'xmlrpc.server',
    'zipapp',
    'zipfile',
    'zipimport',
    'zlib'
]  # type: List[str]
