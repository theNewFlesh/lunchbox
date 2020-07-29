from setuptools import setup

with open('version.txt') as f:
    VERSION = f.read().strip('\n')

with open('prod_requirements.txt') as f:
    PROD_REQUIREMENTS = f.read().split('\n')

with open('dev_requirements.txt') as f:
    DEV_REQUIREMENTS = f.read().split('\n')

with open('README.md') as f:
    README = f.read()
# ------------------------------------------------------------------------------

setup(
    name='lunchbox',
    packages=['lunchbox'],
    version=VERSION,
    license='MIT',
    description='A library of various tools for common python tasks.',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Alex Braun',
    author_email='Alexander.G.Braun@gmail.com',
    url='https://github.com/theNewFlesh/lunchbox',
    download_url='https://github.com/theNewFlesh/lunchbox/archive/' + VERSION + '.tar.gz',
    keywords=['tool', 'tools', 'general'],
    install_requires=PROD_REQUIREMENTS,
    classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.6',
      'Programming Language :: Python :: 3.7',
    ],
    extras_require={
        "dev": DEV_REQUIREMENTS
    },
)
