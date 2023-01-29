from typing import Any, Callable, Dict, List, Optional, Union

from itertools import dropwhile, takewhile
from pathlib import Path
from pprint import pformat
import inspect
import json
import logging
import os
import re
import urllib.request

import wrapt

from lunchbox.enforce import Enforce, EnforceError
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
def log_runtime(
    function, *args, message_=None, _testing=False, log_level='info', **kwargs
):
    # type (Callable, ..., Optional[str], bool, str, ...) -> Any
    r'''
    Logs the duration of given function called with given arguments.

    Args:
        function (function): Function to be called.
        \*args (object, optional): Arguments.
        message_ (str, optional): Message to be returned. Default: None.
        _testing (bool, optional): Returns message if True. Default: False.
        log_level (str, optional): Log level. Default: info.
        \*\*kwargs (object, optional): Keyword arguments.

    Raises:
        EnforceError: If log level is illegal.

    Returns:
        object: function(*args, **kwargs).
    '''
    level = log_level_to_int(log_level)

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

    LOGGER.log(level, message_)
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


def log_level_to_int(level):
    # type: (Union[str, int]) -> int
    '''
    Convert a given string or integer into a log level integer.

    Args:
        level (str or int): Log level.

    Raises:
        EnforceError: If level is illegal.

    Returns:
        int: Log level as integer.
    '''
    keys = ['critical', 'debug', 'error', 'fatal', 'info', 'warn', 'warning']
    values = [getattr(logging, x.upper()) for x in keys]
    lut = dict(zip(keys, values))  # type: Dict[str, int]

    msg = 'Log level must be an integer or string. Given value: {a}. '
    lut_msg = ', '.join([f'{k}: {v}' for k, v in zip(keys, values)])
    msg += f'Legal values: [{lut_msg}].'

    output = 0
    if isinstance(level, int):
        Enforce(level, 'in', values, message=msg)
        output = level

    elif isinstance(level, str):
        level = level.lower()
        Enforce(level, 'in', keys, message=msg)
        output = lut[level]

    else:
        raise EnforceError(msg.format(a=level))

    return output


class LogRuntime:
    '''
    LogRuntime is a class for logging the runtime of arbitrary code.

    Attributes:
        message (str): Logging message with runtime line.
        delta (datetime.timedelta): Runtime.
        human_readable_delta (str): Runtime in human readable format.

    Example:

        >>> import time
        >>> def foobar():
                time.sleep(1)

        >>> with LogRuntime('Foo the bars', name=foobar.__name__, level='debug'):
                foobar()
        DEBUG:foobar:Foo the bars - Runtime: 0:00:01.001069 (1 second)

        >>> with LogRuntime(message='Fooing all the bars', suppress=True) as log:
                foobar()
        >>> print(log.message)
        Fooing all the bars - Runtime: 0:00:01.001069 (1 second)
    '''
    def __init__(
        self,
        message='',  # type: str
        name='LogRuntime',  # type: str
        level='info',  # type: str
        suppress=False,  # type: bool
        message_func=None,  # type: Optional[Callable[[str, StopWatch], None]]
        callback=None,  # type: Optional[Callable[[str], Any]]
    ):
        # type: (...) -> None
        '''
        Constructs a LogRuntime instance.

        Args:
            message (str, optional): Logging message. Default: ''.
            name (str, optional): Name of logger. Default: 'LogRuntime'.
            level (str or int, optional): Log level. Default: info.
            suppress (bool, optional): Whether to suppress logging.
                Default: False.
            message_func (function, optional): Custom message function of the
                signature (message, StopWatch) -> str. Default: None.
            callback (function, optional): Callback function of the signature
                (message) -> Any. Default: None.

        Raises:
            EnforceError: If message is not a string.
            EnforceError: If name is not a string.
            EnforceError: If level is not legal logging level.
            EnforceError: If suppress is not a boolean.
        '''
        Enforce(message, 'instance of', str)
        Enforce(name, 'instance of', str)
        Enforce(suppress, 'instance of', bool)
        # ----------------------------------------------------------------------

        self._message = message
        self._stopwatch = StopWatch()
        self._logger = logging.getLogger(name)
        self._level = log_level_to_int(level)
        self._suppress = suppress
        self._message_func = message_func
        self._callback = callback

    @staticmethod
    def _default_message_func(message, stopwatch):
        # type: (str, StopWatch) -> str
        '''
        Add runtime information to message given StopWatch instance.

        Args:
            message (str): Message.
            stopwatch (StopWatch): StopWatch instance.

        Raises:
            EnforeceError: If Message is not a string.
            EnforceError: If stopwatch is not a StopWatch instance.

        Returns:
            str: Message with runtime information.
        '''
        Enforce(message, 'instance of', str)
        Enforce(stopwatch, 'instance of', StopWatch)
        # ----------------------------------------------------------------------

        msg = f'Runtime: {stopwatch.delta} '
        msg += f'({stopwatch.human_readable_delta})'
        if message != '':
            msg = message + ' - ' + msg
        return msg

    def __enter__(self):
        # type: () -> LogRuntime
        '''
        Starts stopwatch.

        Returns:
            LogRuntime: self.
        '''
        self._stopwatch.start()
        return self

    def __exit__(self, *args):
        # type: (Any) -> None
        '''
        Stops stopwatch and logs message.
        '''
        stopwatch = self._stopwatch
        stopwatch.stop()
        self.delta = self._stopwatch.delta
        self.human_readable_delta = self._stopwatch.human_readable_delta

        msg_func = self._message_func or self._default_message_func
        self.message = msg_func(self._message, stopwatch)

        if not self._suppress:
            self._logger.log(self._level, self.message)

        if self._callback is not None:
            self._callback(str(self.message))


# HTTP-REQUESTS-----------------------------------------------------------------
def post_to_slack(url, channel, message):
    # type (str, str, str) -> urllib.request.HttpResponse
    '''
    Post a given message to a given slack channel.

    Args:
        url (str): https://hooks.slack.com/services URL.
        channel (str): Channel name.
        message (str): Message to be posted.

    Raises:
        EnforceError: If URL is not a string.
        EnforceError: If URL does not start with https://hooks.slack.com/services
        EnforceError: If channel is not a string.
        EnforceError: If message is not a string.

    Returns:
        HTTPResponse: Response.
    '''
    Enforce(url, 'instance of', str)
    Enforce(channel, 'instance of', str)
    Enforce(message, 'instance of', str)
    msg = 'URL must begin with https://hooks.slack.com/services/. '
    msg += f'Given URL: {url}'
    Enforce(
        url.startswith('https://hooks.slack.com/services/'), '==', True,
        message=msg
    )
    # --------------------------------------------------------------------------

    request = urllib.request.Request(
        url,
        method='POST',
        headers={'Content-type': 'application/json'},
        data=json.dumps(dict(
            channel='#' + channel,
            text=message,
        )).encode(),
    )
    return urllib.request.urlopen(request)


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


def _dir_table(obj, public=True, semiprivate=True, private=False, max_width=100):
    # type: (Any, bool, bool, bool, int) -> str
    '''
    Create a table from results of calling dir(obj).

    Args:
        obj (object): Object to call dir on.
        public (bool, optional): Include public attributes in table.
            Default: True.
        semiprivate (bool, optional): Include semiprivate attributes in table.
            Default: True.
        private (bool, optional): Include private attributes in table.
            Default: False.
        max_width (int, optional): Maximum table width: Default: 100.

    Returns:
        str: Table.
    '''
    dirkeys = dir(obj)
    pub = set(list(filter(lambda x: re.search('^[^_]', x), dirkeys)))
    priv = set(list(filter(lambda x: re.search('^__|^_[A-Z].*__', x), dirkeys)))
    semipriv = set(dirkeys).difference(pub).difference(priv)

    keys = set()
    if public:
        keys.update(pub)
    if private:
        keys.update(priv)
    if semiprivate:
        keys.update(semipriv)

    data = [dict(key='NAME', atype='TYPE', val='VALUE')]
    max_key = 0
    max_atype = 0
    for key in sorted(keys):
        attr = getattr(obj, key)
        atype = attr.__class__.__name__
        val = str(attr).replace('\n', ' ')
        max_key = max(max_key, len(key))
        max_atype = max(max_atype, len(atype))
        row = dict(key=key, atype=atype, val=val)
        data.append(row)

    pattern = f'{{key:<{max_key}}}    {{atype:<{max_atype}}}    {{val}}'
    lines = list(map(lambda x: pattern.format(**x)[:max_width], data))
    output = '\n'.join(lines)
    return output


def dir_table(obj, public=True, semiprivate=True, private=False, max_width=100):
    # type: (Any, bool, bool, bool, int) -> None
    '''
    Prints a table from results of calling dir(obj).

    Args:
        obj (object): Object to call dir on.
        public (bool, optional): Include public attributes in table.
            Default: True.
        semiprivate (bool, optional): Include semiprivate attributes in table.
            Default: True.
        private (bool, optional): Include private attributes in table.
            Default: False.
        max_width (int, optional): Maximum table width: Default: 100.
    '''
    print(_dir_table(
        obj,
        public=public,
        semiprivate=semiprivate,
        private=private,
        max_width=max_width,
    ))  # pragma: no cover


def api_function(wrapped=None, **kwargs):
    # type: (Optional[Callable], Any) -> Callable
    r'''
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
