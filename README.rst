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
.. _deno compile: https://docs.deno.com/runtime/reference/cli/compiler/
.. _deno install: https://docs.deno.com/runtime/reference/cli/install/
.. _Django: https://www.djangoproject.com
.. _DJANGO_DEBUG: https://github.com/Dmitri-Sintsov/djk-sample/search?q=DJANGO_DEBUG&type=code
.. _django_deno settings: https://github.com/Dmitri-Sintsov/django-deno/blob/main/django_deno/conf/settings.py
.. _django_deno.lzma: https://github.com/Dmitri-Sintsov/django-deno/blob/main/django_deno/deno/django_deno.lzma
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
.. _server.ts: https://github.com/Dmitri-Sintsov/django-deno/blob/main/django_deno/deno/server.ts
.. _SystemJS: https://github.com/systemjs/systemjs
.. _sucrase: https://github.com/alangpierce/sucrase
.. _terser: https://terser.org
.. _TypeScript: https://www.typescriptlang.org/

`Deno`_ front-end integration for `Django`_, version 0.2.0.

* `rollup.js`_ - bundling for `Django packages static files`_ with importmap resolver.
* `sucrase`_ - optional `TypeScript`_ support.
* `terser`_ - optional compression of bundles.
* The deno server may be extended to support any of deno api, when applicable.
* Uses parts of `drollup`_ code, refactored for Deno v2.

Requirements
------------

* `Deno`_ 2.0.6 or newer.
* `Django`_ 4.2 / Django 5.1 was tested with continuous integration demo app `djk-sample`_.

Installation
------------

In Ubuntu Linux::

    curl -fsSL https://deno.land/install.sh | sh
    export DENO_INSTALL=$HOME/.deno

In Windows run PowerShell then invoke::

    irm https://deno.land/install.ps1 | iex
    set DENO_INSTALL=%userprofile%\.deno

``DENO_INSTALL`` environment variable specifies directory where `Deno`_ is installed.

* In case currently installed `Deno`_ version is older than 2.0.6, please use ``deno upgrade`` command to install the
  newer `Deno`_ version. Deno 1.x is supported only with ``django-deno`` versions lower than 0.2.0.

* This package was tested with Deno version 2.0.6::
  
    deno upgrade --version 2.0.6

The package may work with newer versions of Deno, however it was not tested, thus may fail.

However, since v0.2.0 there is precompiled binary for Linux may be downloaded, which allows to have stable running
enviromnent, see `deno_compile`_ management command.

To install the development version of ``django_deno`` in python3 ``virtualenv``::

    pip install -U git+https://github.com/Dmitri-Sintsov/django-deno.git

To install the stable version of ``django_deno`` in python3 ``virtualenv``::

    pip install -U git+https://github.com/Dmitri-Sintsov/django-deno.git@v0.2.0

Description
-----------

``django_deno`` installs Deno web service which is used to communicate with `Django`_ projects.

Currently the web service `server.ts`_ supports Deno version of `rollup.js`_ bundle generation to automatically provide
`es6 modules`_ bundles for `Django`_ projects, including scripts from `Django packages static files`_.

It's possible to generate `es6 modules`_ bundles and / or `systemjs`_ bundles with optional minification with
`terser`_.

Transpiling of `TypeScript`_ is supported with `sucrase`_. When `sucrase`_ is not enabled, it's expected that the
developing code has es6 imports / exports but the rest of code is written with es5 syntax.

At `Django`_ side ``django_deno`` provides the following `Django management commands`_:

collectrollup
~~~~~~~~~~~~~

* ``collectrollup`` - similar to Django `collectstatic`_ command, but uses `rollup.js`_ to generate Javascript bundles.

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

The additional settings for `rollup.js`_ running `collectrollup`_ management command are specified with
`DENO_ROLLUP_COLLECT_OPTIONS`_ setting, which allows to enable / disable `terser`_ compression and to enable / disable
`sucrase`_ transpiling of `TypeScript`_::

    # Run $VIRTUAL_ENV/djk-sample/cherry_django.py to check the validity of collectrollup command output bundle.
    DENO_ROLLUP_COLLECT_OPTIONS = {
        'sucrase': True,
        'terser': True,
    }

while the default is::

    DENO_ROLLUP_COLLECT_OPTIONS = {
        # 'relativePaths': True,
        'staticFilesResolver': 'collect',
        'sucrase': True,
        'terser': True,
        'bundles': getattr(settings, 'DENO_ROLLUP_BUNDLES', {}),
        'moduleFormat': DENO_OUTPUT_MODULE_FORMATS[DENO_OUTPUT_MODULE_TYPE],
        'syntheticNamedExports': getattr(settings, 'DENO_SYNTHETIC_NAMED_EXPORTS', {}),
    }

* See the complete default settings: `django_deno settings`_

runrollup
~~~~~~~~~

* ``runrollup`` - starts the built-in http development server, similar to Django `runserver`_ command, using `rollup.js`_
  to dynamically generate Javascript bundle in RAM, providing real-time `es6 modules`_ / `TypeScript`_ compatibility for
  older browsers (e.g. IE11).

`DENO_ROLLUP_SERVE_OPTIONS`_ set the `rollup.js`_ options for `runrollup`_ command. The default is::

    DENO_ROLLUP_SERVE_OPTIONS = {
        'inlineFileMap': True,
        # 'relativePaths': True,
        'sucrase': True,
        'preserveEntrySignatures': False,
        'staticFilesResolver': 'serve',
        'withCache': True,
    }

* When ``staticFilesResolver`` is set to ``serve``, `getStaticFilesResolver`_ is used to resolve `Django packages static files`_
  at `Deno`_ side via automatically generated import maps.

deno_compile
~~~~~~~~~~~~
* ``deno_compile`` - compiles built-in `server.ts`_ to ``django_deno`` binary file with `deno compile`_ for the package
  distribution. This management command allows to have stable production running environment. Since v0.2.0 it's a
  preferred way to perform vendoring / bundling of the package.

* Binary compression is supported via ``--compress`` option. github hosted compressed `django_deno.lzma`_ binary
  can be downloaded and extracted automatically, with the following ``settings.py`` value::

    DENO_USE_COMPILED_BINARY = True

deno_install
~~~~~~~~~~~~

* ``deno_install`` management command generates updated `deno install`_ bundle for the built-in deno server. This command
  should be used only for the package updating / redistribution.
* Since Deno v2, it seems to impossible to create the source bundle without remote dependencies
  (see https://github.com/denoland/deno/issues/26488). Thus `deno_compile`_ currently is the preferred way to perform
  vendoring / bundling of the package.

Updating `deno_install`_ should be performed with the following steps:

* Run the project `collectrollup`_ command with the following ``settings.py`` to reload the dependencies::

    DENO_USE_VENDOR = False
    DENO_RELOAD = True
    DENO_CHECK_LOCK_FILE = False

* Run the project `deno_install`_ command to create local `deno install`_::

    python3 manage.py deno_install

* Run the project `collectrollup`_ command with the following ``settings.py``, to use the updated local `deno_install`_::

    DENO_USE_VENDOR = True
    DENO_RELOAD = False
    DENO_CHECK_LOCK_FILE = True

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
