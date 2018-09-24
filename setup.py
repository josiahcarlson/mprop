#!/usr/bin/env python

from distutils.core import setup

try:
    long_description = open('README.rst').read()
except:
    long_description = ''

setup(
    name='mprop',
    version='0.15.0',
    description='Module properties for Python',
    author='Josiah Carlson',
    author_email='josiah.carlson@gmail.com',
    url='https://github.com/josiahcarlson/mprop',
    py_modules=['mprop'],
    classifiers=[
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    license='GNU LGPL v2.1',
    long_description=long_description,
)
