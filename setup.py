#!/usr/bin/env python
# pylint: disable=missing-docstring
# import re
# import ast
from setuptools import setup, find_packages


# def version():
#     version_re = re.compile(r'__version__\s+=\s+(.*)')
#     with open('plpacker/__init__.py', 'rb') as handle:
#         return str(ast.literal_eval(version_re.search(
#             handle.read().decode('utf-8')).group(1)))


def long_description():
    with open('README.rst', 'rb') as handle:
        return handle.read().decode('utf-8')


_TEST_REQUIRE = [
    # coverage 5 is still in alpha.
    'coverage>=4.4.1,<5',
    'pyfakefs>=3.5',
    'pytest-cov>=2.5.1',
    'pytest>=3.0.7',
]

_CI_REQUIRE = [
    'flake8>=3.3.0',
    'pep257>=0.7.0',
    'pylint>=1.7.1',
    'tox>=2.7.0',
]

setup(
    name='ithoughts-quick-notes',
    # version=version(),
    author='Pedro H.',
    author_email='todo@todo',
    description='TODO',
    long_description=long_description(),
    url='https://github.com/digitalrounin/py-lambda-packer.git',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='aws lambda',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    setup_requires=[
        'pytest-runner',
    ],
    install_requires=[],
    tests_require=_TEST_REQUIRE,
    extras_require={
        'ci': _CI_REQUIRE,
        'test': _TEST_REQUIRE,
    },
)
