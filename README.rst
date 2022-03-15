===========
django-deno
===========

.. _collectstatic: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#django-admin-collectstatic
.. _Deno: https://deno.land
.. _deno lock.json: https://deno.land/manual/linking_to_external_code/integrity_checking
.. _deno import_map.json: https://deno.land/manual/linking_to_external_code/import_maps
.. _DENO_OUTPUT_MODULE_TYPE: https://github.com/Dmitri-Sintsov/django-deno/search?l=Python&q=DENO_OUTPUT_MODULE_TYPE&type=code
.. _DENO_ROLLUP_BUNDLES: https://github.com/Dmitri-Sintsov/django-deno/search?q=DENO_ROLLUP_BUNDLES&type=code
.. _DENO_ROLLUP_ENTRY_POINTS: https://github.com/Dmitri-Sintsov/django-deno/search?q=DENO_ROLLUP_ENTRY_POINTS&type=code
.. _DENO_ROLLUP_COLLECT_OPTIONS: https://github.com/Dmitri-Sintsov/django-deno/search?q=DENO_ROLLUP_COLLECT_OPTIONS&type=code
.. _DENO_ROLLUP_SERVE_OPTIONS: https://github.com/Dmitri-Sintsov/django-deno/search?q=DENO_ROLLUP_SERVE_OPTIONS&type=code
.. _deno vendor: https://deno.land/manual/tools/vendor
.. _Django: https://www.djangoproject.com
.. _DJANGO_DEBUG: https://github.com/Dmitri-Sintsov/djk-sample/search?q=DJANGO_DEBUG&type=code
.. _django_deno settings: https://github.com/Dmitri-Sintsov/django-deno/blob/main/django_deno/conf/settings.py
.. _Django management commands: https://docs.djangoproject.com/en/dev/ref/django-admin/
.. _Django packages static files: https://docs.djangoproject.com/en/dev/howto/static-files/
.. _djk-sample: https://github.com/Dmitri-Sintsov/djk-sample
.. _djk-sample settings: https://github.com/Dmitri-Sintsov/djk-sample/blob/master/djk_sample/settings.py
.. _drf-gallery: https://github.com/Dmitri-Sintsov/drf-gallery
.. _drollup: https://deno.land/x/drollup
.. _es6 modules: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules
.. _getStaticFilesResolver: https://github.com/Dmitri-Sintsov/django-deno/search?l=TypeScript&q=getStaticFilesResolver&type=code
.. _isVirtualEntry: https://github.com/Dmitri-Sintsov/django-deno/search?l=TypeScript&q=isVirtualEntry&type=code
.. _setVirtualEntryPoint: https://github.com/Dmitri-Sintsov/django-deno/search?l=TypeScript&q=setVirtualEntryPoint&type=code
.. _rollup.js: https://rollupjs.org/
.. _runserver: https://docs.djangoproject.com/en/dev/ref/django-admin/#runserver
.. _SystemJS: https://github.com/systemjs/systemjs
.. _terser: https://terser.org

`Deno`_ front-end integration for `Django`_, version 0.1.0.

* Currently only `drollup`_ / `terser`_ are supported, the deno server may be extended to support any of deno api, if
  applicable.

Requirements
------------

* Deno 1.19 or newer (which supports `deno vendor`_ command).
* Django 2.2 / Django 3.2 / Django 4.0 is tested with continuous integration demo app `djk-sample`_.

Installation
------------

In Ubuntu Linux::

    curl -fsSL https://deno.land/x/install/install.sh | sh
    export DENO_INSTALL=$HOME/.deno

In Windows run PowerShell then invoke::

    iwr https://deno.land/x/install/install.ps1 -useb | iex

    set DENO_INSTALL=%userprofile%\.deno

``DENO_INSTALL`` environment variable specifies directory where `Deno`_ is installed.

* In case currently installed `Deno`_ version is older than 1.19, please use ``deno upgrade`` command to install the
  latest `Deno`_ version.

To install the development version of ``django_deno`` in python3 ``virtualenv``::

    python -m pip install -U git+https://github.com/Dmitri-Sintsov/django-deno.git

To install the stable version of ``django_deno`` in python3 ``virtualenv``::

    python -m pip install -U git+https://github.com/Dmitri-Sintsov/django-deno.git@v0.1.0

Description
-----------

``django_deno`` installs deno web service which is used to communicate with `Django`_ projects.

Currently the web service supports deno version of `rollup.js`_ bundle (`drollup`_) generation to automatically provide
`es6 modules`_ bundles for `Django`_ projects, including scripts from `Django packages static files`_.

That enables generation of minified `terser`_ bundles and / or `systemjs`_ bundles, the later ones are compatible to
IE11.

Note that currently it supports only `es6 modules`_, not the full transpiling of es5 to es6, so it assumes that
the developing code has es6 imports / exports but the rest of code is written with es5 syntax.

At `Django`_ side it provides the following `Django management commands`_:

collectrollup
~~~~~~~~~~~~~

* ``collectrollup`` - similar to Django `collectstatic`_ command, but uses `drollup`_ to generate Javascript bundles.

It's preferable to run the ``collectrollup`` command this way from the `Django`_ project ``virtualenv``::

    python3 manage.py collectrollup --clear --noinput

``--clear`` option is suggested because the target output may vary depending on the source scripts.

There is `djk-sample`_ script for running ``collectrollup`` in Linux::

    #!/bin/sh
    DJANGO_DEBUG='False' python3 $VIRTUAL_ENV/djk-sample/manage.py collectrollup --noinput --clear

* https://github.com/Dmitri-Sintsov/djk-sample/blob/master/cli/collectrollup.sh

in Windows::

    if not defined DENO_INSTALL (
        set DENO_INSTALL=%USERPROFILE%\.deno
    )
    set "DJANGO_DEBUG=False" & python %VIRTUAL_ENV%/djk-sample/manage.py collectrollup --noinput --clear

* https://github.com/Dmitri-Sintsov/djk-sample/blob/master/cli/collectrollup.cmd

The script also sets the environment variable `DJANGO_DEBUG`_ to ``False`` which is parsed in `djk-sample`_ settings.py::

    DEBUG = os.environ.get('DJANGO_DEBUG', 'true').lower() in TRUE_STR

to set the value of `DENO_OUTPUT_MODULE_TYPE`_ which determines the type of Javascript modules generated, either
``module`` for modern browsers that support es6 natively, or `SystemJS`_ modules, which are compatible with IE11::

    # Do not forget to re-run collectrollup management command after changing rollup.js bundles module type:
    DENO_OUTPUT_MODULE_TYPE = 'module' if DEBUG else 'systemjs-module'

The additional settings for `drollup`_ running `collectrollup`_ management command are specified with
`DENO_ROLLUP_COLLECT_OPTIONS`_ setting, which allows to enable / disable `terser`_ compression::

    # Run $VIRTUAL_ENV/djk-sample/cherry_django.py to check the validity of collectrollup command output bundle.
    DENO_ROLLUP_COLLECT_OPTIONS = {
        'terser': True,
    }

while the default is::

    DENO_ROLLUP_COLLECT_OPTIONS = {
        # 'relativePaths': True,
        # 'staticFilesResolver': True,
        'terser': True,
        'bundles': getattr(settings, 'DENO_ROLLUP_BUNDLES', {}),
        'moduleFormat': DENO_OUTPUT_MODULE_FORMATS[DENO_OUTPUT_MODULE_TYPE],
    }


* For the full default settings: `django_deno settings`_

runrollup
~~~~~~~~~

* ``runrollup`` - starts the built-in http development server, similar to Django `runserver`_ command, using `drollup`_
  to dynamically generate Javascript bundle in RAM, providing real-time `es6 modules`_ compatibility for IE11.

`DENO_ROLLUP_SERVE_OPTIONS`_ set the options for `drollup`_ for `runrollup`_ command, the default is::

    DENO_ROLLUP_SERVE_OPTIONS = {
        'inlineFileMap': True,
        'relativePaths': True,
        'preserveEntrySignatures': False,
        'staticFilesResolver': True,
        'withCache': True,
    }

* When ``staticFilesResolver`` is ``True``, `Django packages static files`_ uses `getStaticFilesResolver`_ at `Deno`_
  server side.

deno_vendor
~~~~~~~~~~~

* ``deno_vendor`` management command generates updated `deno vendor`_ bundle for the built-in deno server. This command
  should be used only for package updating / redistribution.

Updating `deno_vendor`_ should be performed with the following steps:

* Run the project `collectrollup`_ command with the following ``settings.py`` to reload the dependencies::

    DENO_USE_VENDOR = False
    DENO_RELOAD = True
    DENO_CHECK_LOCK_FILE = False

* Run the project `collectrollup`_ command with the following ``settings.py`` to convert `deno lock.json`_ to
  `deno import_map.json`_::

    DENO_USE_VENDOR = False
    DENO_RELOAD = False
    DENO_CHECK_LOCK_FILE = True

* Run the project `deno_vendor`_ command to create local `deno vendor`_::

    python3 manage.py deno_vendor

* Run the project `collectrollup`_ command with the following ``settings.py``, to use the updated local `deno_vendor`_::

    DENO_USE_VENDOR = True
    DENO_RELOAD = False
    DENO_CHECK_LOCK_FILE = True

* Optionally override the vendor dir in the repository and make the commit when necessary.

Bundles
-------
Creation of `rollup.js`_ bundles has two steps, first one is the definition of `Entry points`_, second is the
definition of `Chunks`_. Both are specified in Django project ``settings.py``.

Entry points
~~~~~~~~~~~~
At the first step, one has to specify Javascript entry points with `DENO_ROLLUP_ENTRY_POINTS`_ setting, for example
`djk-sample settings`_::

    DENO_ROLLUP_ENTRY_POINTS = [
        'sample/js/app.js',
        'sample/js/club-grid.js',
        'sample/js/member-grid.js',
    ]

These are the top scripts of es6 module loader hierarchy.

Alternatively, the script may specify ``use rollup`` directive at the first line of Javascript code, which is used for
Django packages entry points and is discouraged for project entry points.

Chunks
~~~~~~

To specify manual bundles / chunks, `DENO_ROLLUP_BUNDLES`_ setting is used. For example `djk-sample settings`_::

    DENO_ROLLUP_BUNDLES = {
        'djk': {
            'writeEntryPoint': 'sample/js/app.js',
            'matches': [
                'djk/js/*',
                'djk/js/lib/*',
                'djk/js/grid/*',
            ],
            'excludes': [],
            'virtualEntryPoints': 'matches',
            'virtualEntryPointsExcludes': 'excludes',
        },
    }

* ``djk`` key specifies the chunk name which will result in generation of ``djk.js`` bundle.
* ``writeEntryPoint`` key specifies main entry point, which is used to generate ``djk.js`` bundle. ``djk.js`` bundle is
  shared among the some / all of `Entry points`_, reducing code redundancy.
* ``matches`` key specifies the list of matching dirs which scripts that will be included into ``djk.js`` bundle.
* ``excludes`` specifies the list of scripts which are excluded from the ``djk.js`` bundle.
* ``virtualEntryPoints`` specifies either the list of dirs or ``matches`` string value to set `es6 modules`_ virtual
  entry points. Such modules are bundled as a virtual ones, included into ``djk.js`` bundle only, not being duplicated
  as separate standalone module files. See `isVirtualEntry`_ / `setVirtualEntryPoint`_ code for more info.

* To see the actual settings / usage, demo apps `djk-sample`_ and `drf-gallery`_ are available.
