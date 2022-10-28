#!/usr/bin/env python3

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
        'version',
        metavar='version',
        type=str,
        nargs=1,
        action='store',
        help='python version',
    )

    parser.add_argument(
        '--prod',
        metavar='prod',
        type=bool,
        default=False,
        nargs=1,
        action='store',
        help='production dependencies only',
    )
    args = parser.parse_args()
    temp, ver, prod = args.template[0], args.version[0], args.prod[0]
    text = generate_pyproject(temp, ver, prod)
    print(text)


def generate_pyproject(source_path, version, prod_mode):
    # type: (str, str, bool) -> str
    '''
    Generate pyproject.toml file given a source_path and python version.
    Removes dev dependecies.

    Args:
        source_path (str): Path to base pyproject.toml file.
        target_path (str): Path to write generated pyproject.toml file.
        version (str): Python version.
        prod_mode (bool): Production dependencies only.

    Returns:
        str: pyproject.toml content.
    '''
    proj = toml.load(source_path)

    # fix python version
    proj['project']['requires-python'] = f'{version}'

    # delete dev dependencies
    if prod_mode:
        del proj['tool']['pdm']['dev-dependencies']['dev']

    return toml.dumps(proj)


if __name__ == '__main__':
    main()
