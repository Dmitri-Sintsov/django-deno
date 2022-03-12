===========
django-deno
===========

.. _collectstatic: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#django-admin-collectstatic
.. _Deno: https://deno.land
.. _deno vendor: https://deno.land/manual/tools/vendor
.. _Django: https://www.djangoproject.com
.. _Django management commands: https://docs.djangoproject.com/en/dev/ref/django-admin/
.. _Django external apps directories: https://docs.djangoproject.com/en/dev/howto/static-files/
.. _djk-sample: https://github.com/Dmitri-Sintsov/djk-sample
.. _drf-gallery: https://github.com/Dmitri-Sintsov/drf-gallery
.. _drollup: https://deno.land/x/drollup
.. _es6 module: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules
.. _rollup.js: https://rollupjs.org/
.. _runserver: https://docs.djangoproject.com/en/dev/ref/django-admin/#runserver
.. _SystemJS: https://github.com/systemjs/systemjs
.. _terser: https://terser.org

`Deno`_ front-end integration for `Django`_, version 0.1.0.

Requirements
------------

* Deno 1.19 or newer (which supports `deno vendor`_ command).
* Django 2.2 / Django 3.2 / Django 4.0 is tested with continuous integration demo app `djk-sample`_.

Installation
------------

Ubuntu Linux::

    curl -fsSL https://deno.land/x/install/install.sh | sh
    export DENO_INSTALL=$HOME/.deno

Windows. Run PowerShell then invoke::

    iwr https://deno.land/x/install/install.ps1 -useb | iex

    set DENO_INSTALL=%userprofile%\.deno

environment variable.

* In case currently installed `Deno`_ version is older than 1.19, please use ``deno upgrade`` command to install the
  latest `Deno`_ version.

Description
-----------

``django_deno`` installs deno web service which is used to communicate with `Django`_ projects.

Currently the web service supports deno version of `rollup.js`_ bundle (`drollup`_) generation to automatically provide
`es6 module`_ bundles for `Django`_ projects, including scripts from `Django external apps directories`_.

That enables generation of minified `terser`_ bundles and / or `systemjs`_ bundles, the later ones are compatible to
IE11.

At `Django`_ side it provides the following `Django management commands`_:

* ``collectrollup`` - similar to Django `collectstatic`_ command, but uses `drollup`_ to generate Javascript bundle.
* ``runrollup`` - similar to Django `runserver`_ command, but uses `drollup`_ to dynamically generate Javascript
  bundle in ram, providing es6 module compatibility for IE11.
* ``deno_vendor`` - generates updated `deno vendor`_ bundle for built-in deno server. Generally should be used only
  for package updating / redistribution.

Note that while currently only `drollup`_ / `terser`_ are supported, the deno server may be extended to support any of
deno api, if applicable.

To see the actual settings / usage, demo apps `djk-sample`_ and `drf-gallery`_ are available.
