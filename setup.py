#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Setup ~/.pypirc at https://packaging.python.org/guides/migrating-to-pypi-org/
# python setup.py bdist_wheel
# pip3 install -U setuptools wheel twine
# twine upload -r test dist/django_deno-0.2.0-py2.py3-none-any.whl

import os
import sys

import django_deno

from setuptools import setup, find_namespace_packages

version = django_deno.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on github:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

lines = []
with open('README.rst', 'r') as readme_file:
    for line in readme_file:
        # Do not include github relative links which are not parsed by pypi.
        if '.. github relative links' in line:
            break
        else:
            lines.append(line)

readme = ''.join(lines)

# http://stackoverflow.com/questions/14399534/how-can-i-reference-requirements-txt-for-the-install-requires-kwarg-in-setuptool
with open('requirements.txt', 'r') as f:
    install_reqs = [
        s for s in [
            line.split('#', 1)[0].strip(' \t\n') for line in f
        ] if s != ''
    ]

packages = find_namespace_packages(
    include=['django_deno', 'django_deno.*'],
)

setup(
    name='django-deno',
    version=version,
    description="""Deno front-end integration for Django""",
    long_description=readme,
    long_description_content_type='text/x-rst',
    author='Dmitriy Sintsov',
    author_email='questpc256@gmail.com',
    url='https://github.com/Dmitri-Sintsov/django-deno',
    packages=packages,
    include_package_data=True,
    install_requires=install_reqs,
    license="LGPL-3.0",
    zip_safe=False,
    keywords='django deno rollup swc sucrase typescript runserver collectstatic'.split(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    setup_requires=['setuptools', 'wheel'],
)
