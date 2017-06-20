from setuptools import setup

from bargain import __version__


setup(
    name='bargain',
    version=__version__,
    description='Serverless cryptocurrency trading bot',

    author='Matteo De Wint',
    author_email='matteodewint@gmail.com',
    url='https://bitbucket.org/mdwint/bargain',

    packages=['bargain'],

    install_requires=[
        'PyYAML',
        'requests',
    ],

    entry_points={'console_scripts': ['bargain=bargain.main:cli_handler']},
)
