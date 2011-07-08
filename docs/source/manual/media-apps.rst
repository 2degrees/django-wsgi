=======================
Serving media à la WSGI
=======================

Until now, the most common approach to serving static files (aka "media") in
Django is to serve it from your application if you're running the development
server (i.e., by adding an entry to a ``URLConf`` with a built-in view), and
let the Web server do it in deployment.

The main disadvantage of this approach is that the development environment
becomes less similar to what you will have in production. If you're not going
to be serving static files on the final site, why serve them in the development
machines?

To work around this, you can have a WSGI application serving your media, so your
application will only serve your own views, just like you'd do in production.
There are some WSGI applications out there that serve static files which
you can take and configure, but *twod.wsgi* has a function to configure one
of them (:class:`paste.urlparser.StaticURLParser`) based on your ``MEDIA_ROOT``
and ``MEDIA_URL`` settings.

Using it is very easy, absolutely reliable and compatible with anything you
may have now. And it's also able to serve the media for Django Admin.
It will always call your application, unless the requested path begins with
``MEDIA_URL`` or ``ADMIN_MEDIA_PREFIX``.

**This is something optional**. When used under a multi-threaded server like
PasteScript, it should be even faster given that nothing from Django gets
run while serving the static files.

Configuring it from a PasteDeploy file will always take 3 additional lines:

.. code-block:: ini

    # ...
    
    [composite:full_app]
    use = egg:twod.wsgi#full_django
    django_app = myapp
    
    # ...

``django_app`` represents your Django application, which can be:

- The name of an ``app:`` section in the same configuration file, where this
  application is configured.
- The URI to an application in another PasteDeploy configuration file (e.g.,
  "config:/path/to/config.ini", "config:/path/to/config.ini#develop").
- The URI to an entry point for a PasteDeploy application factory (e.g.,
  "egg:yourpackage#entry_point").

You'll then need to make sure you load ``full_app`` instead of ``myapp``, since
the latter is presumably no longer able to serve media. To that end, you may
consider renaming ``composite:full_app`` to ``composite:main``.


Setting up the media programatically
====================================

If for some reason you need to set this up from your Python code, you can use
the :func:`twod.wsgi.factories.add_media_to_app` function::

    from paste.deploy import loadapp
    from twod.wsgi.factories import add_media_to_app
    
    # The Django-powered application, with no media:
    django_app = loadapp("config:/path/to/config.ini")
    
    # The Django-powered application plus the media:
    full_app = add_media_to_app(django_app)


This would be particularly useful if you'd like to serve static files from more
than one directory::

    from paste.urlparser import StaticURLParser
    
    full_app['/css'] = StaticURLParser("/path/to/the/css/directory")
    full_app['/js'] = StaticURLParser("/path/to/the/js/directory")

Of course, this would be something you'd do on your development servers. In
production environments it's always best to leave the server serve the static
files.
