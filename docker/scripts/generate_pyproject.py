#!/usr/bin/env python3
from typing import Any, List

import argparse

import toml
# ------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description='Generates a pyproject.toml file for specific python version',
        usage='\ngenerate_pyproject [template] [python-version] [-h --help]'
    )

    parser.add_argument(
        'template',
        metavar='template',
        type=str,
        nargs=1,
        action='store',
        help='pyrpoject.toml filepath',
    )

    parser.add_argument(
        '--replace',
        metavar='replace',
        type=str,
        nargs='+',
        default=[],
        action='append',
        help='python version',
    )

    parser.add_argument(
        '--delete',
        metavar='delete',
        type=str,
        nargs='+',
        default=[],
        action='append',
        help='python version',
    )

    args = parser.parse_args()
    template, repls, dels = args.template[0], args.replace, args.delete
    repls = [x[0].split(',') for x in repls]
    dels = [x[0] for x in dels]
    text = generate_pyproject(template, repls, dels)
    print(text)


class PyprojectEncoder(toml.TomlArraySeparatorEncoder):
    def __init__(self, _dict=dict, preserve=False, separator=','):
        super().__init__(_dict, preserve, ',\n   ')

    def dump_list(self, v):
        if len(v) == 0:
            return '[]'
        if len(v) == 1:
            return '["' + v[0] + '"]'
        output = super().dump_list(v)[1:-1].rstrip('    \n')
        return '[\n   ' + output + '\n]'


def generate_pyproject(filepath, replacements, deletions):
    # type: (str, List[List[str, Any]], List[str]) -> str
    '''
    Generate an new pyproject.toml file from a given one and a list of
    replacements and deletions.

    edits a

    Args:
        filepath (str): pyproject.toml filepath.
        replacements (List[List[str, object]]): LIst of key value pairs.
            Key is replaced with value.
        deletions (List[str]): Keys to be deleted.

    Returns:
        str: pyproject.toml content.
    '''
    data = toml.load(filepath)

    def lookup(key, data):
        keys = key.split('.')
        last_key = keys.pop()
        temp = data
        for k in keys:
            temp = temp[k]
        return temp, last_key

    for key, val in replacements:
        temp, k = lookup(key, data)
        temp[k]= val

    for key in deletions:
        temp, k = lookup(key, data)
        del temp[k]

    return toml.dumps(data, encoder=PyprojectEncoder())


if __name__ == '__main__':
    main()
