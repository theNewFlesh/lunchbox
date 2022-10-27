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
    args = parser.parse_args()
    text = generate_pyproject(args.template[0], args.version[0])
    print(text)


def generate_pyproject(source_path, version):
    # type: (str, str) -> str
    '''
    Generate pyproject.toml file given a source_path and python version.
    Removes dev dependecies.

    Args:
        source_path (str): Path to base pyproject.toml file.
        target_path (str): Path to write generated pyproject.toml file.
        version (str): Python version.

    Returns:
        str: pyproject.toml content.
    '''
    proj = toml.load(source_path)

    # fix python version
    proj['project']['requires-python'] = f'^{version}'

    # delete dev dependencies
    del proj['tool']['pdm']['dev-dependencies']['dev']

    return toml.dumps(proj)


if __name__ == '__main__':
    main()
