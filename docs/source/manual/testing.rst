===============================
WSGI testing for Django in Nose
===============================

Testing Django applications requires setting up an appropriate environment,
which is a generic procedure. If you're using `Nose
<http://somethingaboutorange.com/mrl/projects/nose/>`_ and a
:doc:`paste-factory`, you can use a Nose plugin that will simplify this setup.
You just have to use the following option:

.. program:: nosetests

.. cmdoption:: --with-django-wsgified=<URI-to-PasteDeploy-config>

For example:

.. code-block:: bash

    nosetests --with-django-wsgified=config:/path/to/configuration.ini

The big advantage of this is that you'll be able to run the test suite with
different settings (e.g., to change the database backend).

If you don't want to type that long option all the time, you can add the following
to your :file:`setup.cfg` file (should be in the same directory as
:file:`setup.py`):

.. code-block:: ini

    [nosetests]
    with-django-wsgified = config:/path/to/configuration.ini

And then you'll just need to run :command:`nosetests`.


Buildout recipe
===============

Hard-coding the URI in a file is an option when it's a fixed and relative path.
If that's not the case and you use `Buildout <http://www.buildout.org/>`_
[#use-buildout]_, our recipe for the Nose plugin will solve this issue.

You could use it like this:

.. code-block:: ini

    [test]
    recipe = twod.wsgi:nose
    paste_config_uri = ${URI_to_the_config}
    eggs = YOUR_DISTRIBUTION

Then it will create a :command:`nosetests` script where the
:option:`--with-django-wsgified` will be set to the value in the Buldout
variable ``${URI_to_the_config}`` by default. You'll be able to override this
URI when you run :command:`nosetests`, if you ever need to.

It's an extension to the `zc.recipe.egg <http://pypi.python.org/pypi/zc.recipe.egg>`_
recipe, so you can use its additional options such as ``extra-paths`` and
``find-links``.

.. note::

    **Make sure to install the extra dependencies for this recipe.**
    
    If you've added ``twod.wsgi`` as a dependency in your :file:`setup.py` file,
    rename it to ``twod.wsgi[buildout]``. This way, *twod.wsgi* will be
    installed along with the additional dependencies for this Buildout recipe.
    
    If you're installing it from :command:`easy_install`, you'd need to run::
    
        easy_install twod.wsgi[buildout]


Functional tests with WebTest
=============================

`WebTest <http://pythonpaste.org/webtest/>`_ is a `functional testing
<http://en.wikipedia.org/wiki/Functional_testing>`_ library
for WSGI applications. It's like the one provided by Django, but better. Among
other things, it's able to parse HTML, XML and JSON responses so you can
inspect them pythonically.

To use it, you'd just need to wrap our Django-powered WSGI application around
:class:`webtest.TestApp`::

    from webob import TestApp
    from twod.wsgi import DjangoApplication
    
    app = TestApp(DjangoApplication())
    
    # ...
    
    response = app.get("/")
    
    assert "Welcome to my site" in response
    assert 200 == response.status_int
    assert "200 Alright then" == response.status
    assert "login" in response.forms

The test application object is stateless, so it's safe to reuse the same object
for all your tests.

Skipping database setup
=======================

By default, it is going to set up a test database. If you want to run a test
suite which does not need a database, you can disable it with the :option:`--no-db`
option:

.. program:: nosetests

.. cmdoption:: --no-db
    Do not create a test database in Django.

For example::

    nosetests --no-db your_packages.tests.test_suite_without_db


.. rubric:: Footnotes

.. [#use-buildout] You should be using Buildout anyway!
