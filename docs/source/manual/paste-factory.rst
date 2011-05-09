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
    django_settings_module = your_application.settings
    
    [app:main]
    use = egg:twod.wsgi

It does not define any option that can be used by Django or your application,
apart from ``debug``. Note this option is lower case: That's the de-facto
spelling for this variable in the WSGI world. *twod.wsgi* will automatically
set Django's ``DEBUG`` to that value.

The ``DEFAULT`` section is the only special section in these configuration
files. There you can define variables to be used across the different modes
in which your application can be run, as well as some meta variables for Paste,
*twod.wsgi* or other 3rd party software. Sections with the ``app:`` prefix
define the settings for WSGI applications; you should generally use this kind of
sections for your settings.

You can have more than one set of settings for your Django application. If,
for example, you wanted to be able to use your application in development and
deployment mode, you could use a configuration like this:

.. code-block:: ini

    [DEFAULT]
    debug = False
    django_settings_module = your_application.settings
    
    [app:main]
    use = egg:twod.wsgi
    
    [app:development]
    use = main
    set debug = True

Because we need to toggle the value of ``DEBUG`` from the configuration file,
you must remove this variable from your settings module. If you have variables
which depend on this value, you can still refer to it like this:

.. code-block:: ini

    [DEFAULT]
    debug = False
    django_settings_module = your_application.settings
    
    [app:main]
    use = egg:twod.wsgi
    TEMPLATE_DEBUG = %(debug)s
    
    [app:development]
    use = main
    set debug = True
    
Or, you can override them on a per application basis:

.. code-block:: ini

    [DEFAULT]
    debug = False
    django_settings_module = your_application.settings
    
    [app:main]
    use = egg:twod.wsgi
    TEMPLATE_DEBUG = False
    
    [app:development]
    use = main
    set debug = True
    # TEMPLATE_DEBUG will equal "False" unless we override it:
    TEMPLATE_DEBUG = True


You can then use the values the same way you've been doing it, with Django's
``settings`` object or the old-way (importing your settings module directly)::

    from django.conf import settings
    
    print settings.DEBUG

This mechanism can be used to complement your settings module or replace it
completely (as long as you don't use `unsupported settings`_, which must still
be set in Python code).


Django settings
===============

PasteDeploy passes all the values as strings, so you have to convert them into
the right Python type by hand; possibly using the :mod:`conversion utilities
<paste.deploy.converters>` it provides. That's not necessary with the
`official settings in Django
<http://docs.djangoproject.com/en/dev/ref/settings/>`_ because *twod.wsgi* will
convert them automatically, and you can also have your own settings converted
too.

You can move all your settings to this INI file or only those which should
be variable eventually. It's up to you. The author believes it's best to move
it all to the convenient INI file, except for those settings which are not
really settings, but a crucial component of your application (e.g.,
``TEMPLATE_LOADERS``, ``MIDDLEWARE_CLASSES``, ``FILE_UPLOAD_HANDLERS``,
``INSTALLED_APPS``)


Strings
-------

Because everything is a string unless told otherwise, no extra step is required
to use them. You should however keep in mind that quotes should not be used to
delimit values -- Any quote you put in there will be part of the string.

Examples:

.. code-block:: ini
    
    [app:main]
    use = egg:twod.wsgi
    
    # Single line option:
    MY_SHORT_STRING = foo
    
    MULTI_LINE = This
        is a
        multi-line
        option
    
    # Pound signs are included:
    ANOTHER_STRING = Room #12
    
    QUOTED_STRING = "Lorem ipsum"


Booleans
--------

Boolean settings in Django like ``TEMPLATE_DEBUG`` will be converted
automatically, and if you want your boolean settings to be converted
automatically too, you can list them all in the ``DEFAULT`` section:

.. code-block:: ini

    [DEFAULT]
    # ...
    twod.booleans =
        MY_BOOL1
        MY_BOOL2
    # ...
    
    [app:main]
    use = egg:twod.wsgi
    # ...
    MY_BOOL1 = True
    MY_BOOL2 = False
    # ...

Boolean keywords are case-insensitive in PasteDeploy, and you can even use
other keywords like ``yes`` or ``no``.

Integers
--------

Django integer settings like ``EMAIL_PORT`` and ``DATABASE_PORT`` will get
converted automatically if they're set. Use the ``twod.integers`` option to
have yours converted too:

.. code-block:: ini

    [DEFAULT]
    # ...
    twod.integers =
        MY_INT
    # ...
    
    [app:main]
    use = egg:twod.wsgi
    # ...
    
    # Built-in integer:
    DATABASE_PORT = 5432
    
    # Custom integer:
    MY_INT = 86400
    
    # ...
    


Tuples
------

Again, built-in tuple settings in Django are converted automatically. To have
your tuples converted too, use the ``twod.tuples`` option in the ``DEFAULT``
section:

.. code-block:: ini

    [DEFAULT]
    # ...
    twod.tuples =
        COLLECTION1
        COLLECTION2
        COLLECTION3
    # ...
    
    [app:main]
    use = egg:twod.wsgi
    # ...
    
    # Single line:
    COLLECTION1 = Oxford London Liverpool Leeds Manchester
    
    # Multi line:
    COLLECTION2 =
        Oxford
        London
        Liverpool
        Leeds
        Manchester
        
    # Mixed:
    COLLECTION3 = Oxford London
        Liverpool Leeds
        Manchester
    
    # ...

Items should be delimited by whitespace.

Note that when you have one of these settings is already defined in your
Python settings module, *twod.wsgi* will append the items found in the INI file
to the existing tuple. For example, if you define the following tuple in your
settings module::

    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    )

And have the following configuration:

.. code-block:: ini

    # ...
    
    [app:main]
    use = egg:twod.wsgi
    
    MIDDLEWARE_CLASSES =
        yourpackage.middleware.ExtraMiddleware1
        yourpackage.middleware.ExtraMiddleware2
    
    # ...

The ``MIDDLEWARE_CLASSES`` setting will end up having the following value::

    tuple(
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'yourpackage.middleware.ExtraMiddleware1',
        'yourpackage.middleware.ExtraMiddleware2',
    )


Nested tuples
-------------

Django's nested tuple settings (e.g., ``ADMINS``) are converted automatically
and custom settings can be converted using the ``twod.nested_tuples``:

.. code-block:: ini

    [DEFAULT]
    # ...
    twod.nested_tuples =
        YOUR_NESTED_TUPLE
    # ...
    
    [app:main]
    use = egg:twod.wsgi
    # ...
    ADMINS =
        Gustavo ; foo@example.com
    
    YOUR_NESTED_TUPLE =
        Europe ; Madrid
        Europe ; Oxford
        Asia ; Tokyo
    
    # ...


Dictionaries
------------

Dictionaries can be used almost the same way you use `nested tuples`_:

.. code-block:: ini

    [DEFAULT]
    # ...
    twod.dictionaries =
        YOUR_DICTIONARY
    # ...
    
    [app:main]
    use egg:twod.wsgi
    # ...
    
    # Built-in dictionary -- will get converted automatically:
    DATABASE_OPTIONS =
        sslmode=require
    
    # Custom dictionary; whitespace surrounding the equals sign is ignored:
    YOUR_DICTIONARY =
        France=Paris
        Spain = Madrid
        UK= London
        Venezuela = Caracas
    
    # ...


Unsupported settings
--------------------

The following options are not converted automatically, yet:

- ``FILE_UPLOAD_PERMISSIONS``.
- ``LANGUAGES``.
- ``MESSAGE_TAGS``.
- ``SERIALIZATION_MODULES``.

New settings introduced in Django 1.2 are not supported yet either.

So, if you need to use them, you would need to define them in your settings
module or create your own factory (see below) to convert the values by
yourself.


Implicit variables
==================

There's a variable implicitly set by PasteDeploy: ``here``, which is the
absolute path to the directory that contains the INI file. You can use it like
this:

.. code-block:: ini

    # ...
    
    [app:main]
    use = egg:twod.wsgi
    MEDIA_ROOT = %(here)s/media
    
    # ...

The other variable is ``__file__``, which is the absolute path to the INI
file. It's not very useful in the context of these files, but can be useful
while `using custom factories`_.


Serving your application
========================

Serving your application is a piece of cake now that you use PasteDeploy. It's
simpler than using Django's mechanisms because there's no need to import
:mod:`os` and set an environment variable.


Deployment
----------

The following is a sample WSGI script for *mod_wsgi*::

    from paste.deploy import loadapp
    
    application = loadapp("config:/path/to/your/config.ini")

And the following is a sample script for FastCGI::

    from paste.deploy import loadapp
    from flup.server.fcgi_fork import WSGIServer
    
    app = loadapp("config:/path/to/your/config.ini")
    WSGIServer(app).run()

Sorry for making your deployment boring!

You might want to check the deployment documentation for the other Python
frameworks (e.g., Pylons). They've been using WSGI heavily since day one,
so it's likely you'll get ideas on how to meet your special needs, should you
have any.


Development server
------------------

Django's development server is only able to serve the current Django application
using its so-called "handler" with limited WSGI support, so you won't be able
to use :command:`manage runserver` anymore. But don't panic! You'll be able to
use a better development server now.

You can use any WSGI compliant server and serve your application with the
settings you want to use in development mode. So you could use Apache for
development, for example, but we've fortunately left the PHP era behind.

There are a few WSGI servers that are very convenient for development of WSGI
application and `PasteScript <http://pythonpaste.org/script/>`_ is by far the
most widely used one. Unlike Django's, it is multi-threaded and thus `suitable
for AJAX stuff <http://code.djangoproject.com/ticket/3357>`_. Like Django's,
it's able to reload the application when you change something in your code.
It's also so robust that it's often the server of choice for people deploying
with FastCGI.

Once you have installed PasteScript (e.g., :command:`easy_install PasteScript`),
you need to configure the server in your configuration file by adding the
following section anywhere:

.. code-block:: ini

    [server:main]
    use = egg:Paste#http
    port = 8080

And then you'll be able to run the server::

    cd /path/to/your/project
    paster serve --reload config.ini

:command:`paster` will load the application defined in ``app:main``. If you
want to use a different one, you'd need to set it explicitly, e.g.::

    paster serve --reload config.ini#develop

If you don't want to type that long command all the time, you could just
`execute that file directly <http://pythonpaste.org/script/#scripts>`_.


Configure logging
~~~~~~~~~~~~~~~~~

You can configure logging from the same PasteDeploy configuration file by
adding all `the sections recognized by Python's built-in logging mechanisms
<http://docs.python.org/library/logging.html#configuration-file-format>`_.

A full development configuration file could look like this:

.. code-block:: ini
    
    [server:main]
    use = egg:Paste#http
    port = 8000
    
    [app:main]
    use = config:base-config.ini
    set debug = True
    
    # ===== LOGGING
    
    [loggers]
    keys = root,yourpackage
    
    [handlers]
    keys = global,yourpackage
    
    [formatters]
    keys = generic
    
    # Loggers
    
    [logger_root]
    level = WARNING
    handlers = global
    
    [logger_yourpackage]
    qualname = coolproject.module
    handlers = yourpackage
    propagate = 0
    
    # Handlers
    
    [handler_global]
    class = StreamHandler
    args = (sys.stderr,)
    level = NOTSET
    formatter = generic
    
    [handler_yourpackage]
    class = handlers.RotatingFileHandler
    args = ("%(here)s/logs/coolpackage.log", )
    level = NOTSET
    formatter = generic
    
    # Formatters
    
    [formatter_generic]
    format = %(asctime)s,%(msecs)03d %(levelname)-5.5s [%(name)s] %(message)s
    datefmt = %Y-%m-%d %H:%M:%S


Making :command:`manage` work again
===================================

You'll find that your :command:`manage` command will be broken after moving
settings over to a PasteDeploy configuration file. The fix is really simple,
just put the following at the top of your :command:`manage` script::

    from paste.deploy import loadapp
    
    loadapp("config:/path/to/your/configuration.ini")


PasteDeploy and Buildout
------------------------

If you're using `Buildout <http://www.buildout.org/>`_, you may want to use
the `zc.recipe.egg:scripts <http://pypi.python.org/pypi/zc.recipe.egg>`_
recipe to preppend the initialisation code to your scripts. It'd be a powerful
tool when your application may be run in different modes.

For example, we're using it like this:

.. code-block:: ini

    [buildout]
    parts = scripts
    
    # ...
    
    [scripts]
    recipe = zc.recipe.egg:scripts
    eggs =
        ipython
        OUR_DISTRIBUTION
        sphinx
    initialization = from paste.deploy import loadapp; loadapp("${vars:config_uri}")
    # "manage" is defined in OUR_DISTRIBUTION
    scripts = 
        ipython
        manage
        sphinx-build
    
    [vars]
    config_uri = config:${buildout:directory}/config.ini
    
    # ...

.. tip::
    If you want to share settings between your PasteDeploy and Buildout
    configuration files, check `DeployRecipes
    <http://packages.python.org/deployrecipes/>`_.

Multiple configuration files
============================

As we've seen so far, PasteDeploy configuration files can be extended in a
cascade like fashion. This can also be done across files.

You could have the following base configuration file:

.. code-block:: ini

    # base-config.ini
    
    [DEFAULT]
    debug = False
    
    [app:base]
    use = egg:twod.wsgi
    EMAIL_PORT = 25
    
    [app:debug]
    use = base
    set debug = True

And then override it for development:

.. code-block:: ini

    # develop.ini
    
    [server:main]
    use = egg:Paste#http
    port = 8080
    
    [app:main]
    use = config:base-config.ini#debug
    EMAIL_PORT = 1025

This way, you could also run :command:`paster` as::

    paster serve --reload develop.ini


Using custom factories
======================

If you need to perform a one-off routine when your application is started up
(i.e., before any request), you can write your own PasteDeploy application
factory::

    from twod.wsgi import wsgify_django
    
    
    def make_application(global_config, **local_conf):
        
        # Do something before importing Django and your settings have been applied.
        
        app = wsgify_django(global_config, **local_conf)
        
        # Do something right after your application has been set up (e.g., add WSGI middleware).
        
        return app

``global_config`` is a dictionary that contains all the options in the ``DEFAULT``
section, while ``local_conf`` will contain all the options in the ``app:*``
section.

PasteDeploy offers two options to use application factories in a configuration
file:

- **Setuptools entry point**: If you add the following to your :file:`setup.py`
  file::
  
      setup("yourdistribution",
        # ...
        entry_points="""
        # -*- Entry points: -*-
        [paste.app_factory]
        main = yourpackage.module:make_application
        """,
      )
   
  you'd be able to use the factory as:
  
  .. code-block:: ini
  
      # ...
      [app:main]
      use = egg:yourdistribution
      # ...
   
- If you can't or don't want to define an entry point, you can use it like this:

  .. code-block:: ini
  
      # ...
      [app:main]
      paste.app_factory = yourpackage.module:make_application
      # ...

