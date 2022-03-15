#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Setup ~/.pypirc at https://packaging.python.org/guides/migrating-to-pypi-org/
# python setup.py sdist
# pip3 install twine
# twine upload -r test dist/django-deno-0.1.0.tar.gz

import os
import sys

import django_deno

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

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

setup(
    name='django-deno',
    version=version,
    description="""Deno front-end integration for Django""",
    long_description=readme,
    long_description_content_type='text/x-rst',
    author='Dmitriy Sintsov',
    author_email='questpc256@gmail.com',
    url='https://github.com/Dmitri-Sintsov/django-deno',
    packages=[
        'django_deno',
    ],
    include_package_data=True,
    install_requires=install_reqs,
    license="LGPL-3.0",
    zip_safe=False,
    keywords='django deno rollup runserver collectstatic'.split(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    setup_requires=['wheel'],
)
