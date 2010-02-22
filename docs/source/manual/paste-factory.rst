==========================================
PasteDeploy Application Factory for Django
==========================================

`Paste <http://pythonpaste.org/>`_ is an umbrella project for widely used
WSGI-related packages, as well as the name of a meta-framework part of that
project.

One of these projects is `PasteDeploy <http://pythonpaste.org/deploy/>`_,
whose purpose can be implied by its name. Put simply, it offers a very flexible
configuration mechanism (based on `INI files
<http://en.wikipedia.org/wiki/INI_file>`_) to set up your application which
can also give you full control over this initialisation by means of Python code.
It's not only used to set up the application in deployment mode, but also in
development mode.

The way it works is very simple: You define a callable which takes all the
configuration options as arguments and returns a WSGI application object (which
in this case would be a Django application). These callables are called
"Application Factories", while Django refers to the WSGI application object
as "WSGI handler" or "handler" for short.

If you don't need to run any initialisation routine, you can have PasteDeploy
use the generic Application Factory provided by *twod.wsgi*. If you do, you
can define your own factory. Either way, all these options will be available
as settings within Django.

The following is a minimal configuration file which uses the Application Factory
provided by *twod.wsgi*.

.. code-block:: ini

    [DEFAULT]
    debug = False
    
    [app:main]
    use = egg:twod.wsgi
    django_settings_module = your_application.settings

It does not define any option that can be used by Django or your application,
apart from ``debug``. Note this option is lower case: That's the de-facto
spelling for this variable in the WSGI world. *twod.wsgi* will automatically
set Django's ``DEBUG`` to that value.

The ``DEFAULT`` section is the only special section in these configuration
files. There you can define variables to be used across the different modes
in which your application can be run, as well as some meta variables for Paste,
*twod.wsgi* or other 3rd party software. Sections with the ``app:`` prefix
define the settings for WSGI applications.

You can have more than one set of settings for your Django application. If,
for example, you wanted to be able to use your application in development and
deployment mode, you could use a configuration like this:

.. code-block:: ini

    [DEFAULT]
    debug = False
    
    [app:main]
    use = egg:twod.wsgi
    django_settings_module = your_application.settings
    
    [app:development]
    use = main
    set debug = True

Because we need to toggle the value of ``DEBUG`` from the configuration file,
you must remove this variable from your settings module. If you have variables
which depend on this value, you can still refer to it like this:

.. code-block:: ini

    [DEFAULT]
    debug = False
    
    [app:main]
    use = egg:twod.wsgi
    django_settings_module = your_application.settings
    TEMPLATE_DEBUG = %(debug)s
    
    [app:development]
    use = main
    set debug = True
    
Or, you can override them on a per application basis:

.. code-block:: ini

    [DEFAULT]
    debug = False
    
    [app:main]
    use = egg:twod.wsgi
    django_settings_module = your_application.settings
    TEMPLATE_DEBUG = False
    
    [app:development]
    use = main
    set debug = True
    # TEMPLATE_DEBUG will equal "False" unless we override it:
    TEMPLATE_DEBUG = True


You can then use the values the same way you've been doing so, with Django's
``settings`` object or the old-way (importing your settings module directly)::

    from django.conf import settings
    
    print settings.DEBUG

This mechanism can be used to complement your settings module or replace it
completely (as long as you don't use `unsupported settings`_, which must still
be set in Python code).


Implicit variables
==================

There's a variable implicitly set by PasteDeploy: ``here``, which is the
absolute path to the directory that contains the INI file. You can use it like
this:

.. code-block:: ini

    # ...
    
    [app:main]
    use = egg:twod.wsgi
    django_settings_module = your_application.settings
    MEDIA_ROOT = %(here)s/media
    
    # ...

The other variable is ``__file__``, which is the absolute path to the INI
file. It's not very useful in the context of these files, but can be useful
while `using custom factories`_.


Serving your application
========================

Deployment
----------

Development server
------------------

PasteScript.


Using custom factories
======================


Typecasting
===========

Booleans
--------

Lists
-----

Nested lists
------------

Dictionaries
------------


Unsupported settings
====================


Setting up logging
==================


Loading the settings outside of Paste
=====================================

    from paste.deploy import loadapp
    
    loadapp("config:/path/to/your/configuration.ini")
    # or,
    loadapp("config:/path/to/your/configuration.ini#development")
