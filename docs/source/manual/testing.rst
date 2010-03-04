===============================
WSGI testing for Django in Nose
===============================

Testing Django applications requires setting up an appropriate environment,
which is a generic procedure. If you're using `Nose
<http://somethingaboutorange.com/mrl/projects/nose/>`_ and a
:doc:`paste-factory`, you can use a Nose plugin that will simplify this setup.

To use it, you just need to pass the URI to the PasteDeploy configuration file,
like this:

.. code-block:: bash

    nosetests --

The big advantage of this is that you'll be able to run the test suite with
different settings (e.g., to change the database backend).

If you don't want to type that long option all the time, you can add the following
to your :file:`setup.cfg` file (should be in the same directory as
:file:`setup.py`):

.. code-block:: ini

    [nosetests]
    with-django-wsgified=config:/path/to/configuration.ini

And then you'll just need to run :command:`nosetests`.


Buildout recipe
===============

.. note::

    **Make sure to install the extra dependencies for this recipe.**
    
    If you've added ``twod.wsgi`` as a dependency in your :file:`setup.py` file,
    rename it to ``twod.wsgi[buildout]``. This way, *twod.wsgi* will be
    installed along with the additional dependencies for this Buildout recipe.
    
    If you're installing it from :command:`easy_install`, you'd need to run::
    
        easy_install twod.wsgi[buildout]


Functional tests with WebTest
=============================


Skipping database setup
=======================
