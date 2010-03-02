===========================
Embedding WSGI applications
===========================

The other WSGI frameworks support running external applications from within
the current WSGI application and Django does now thanks to *twod.wsgi*. This
gives you the ability to serve 3rd party applications on-the-fly, as well as
control the requests they get and the responses they return (in order to
filter them or replace them completely).

.. note::

    Django people distinguish "projects" from "applications". From a WSGI point
    of view, those so-called "Django projects" are "WSGI applications" and the
    so-called "Django applications" are just a framework-specific thing with no
    equivalent.
    
    To keep things simple while using the right WSGI terminology,
    Django-powered WSGI applications are referred to as "Django applications"
    within this documentation.


Embedding non-Django applications
=================================

You can mount WSGI applications directly in your Django URL configuration, or
call them from a view to filter the requests they get and/or the response they
return.

Mounting them as Django views
-----------------------------


Calling them from a Django view
-------------------------------


.. warning:: **Avoid reading the body of a request!**
    
    The body of some responses may be generators, which are useful when the
    response is big that has to be sent in chunks (e.g., a video).
    If you read their body, you would consume it and thus you would also alter
    the status of said body.
    
    If you do need to read it, check the ``Content-Type`` first to make sure
    that's what you're looking for. If it really is, and the body is a
    generator, make sure to pass on a proper response body.
    
    Note it's absolutely fine to deal with the response status and headers,
    though.


Embedding Django applications
=============================

Unfortunately, Django has some design errors that prevent two or more
Django applications from living in the same process; namely, the
:envvar:`DJANGO_SETTINGS_MODULE` variable and global variables like
:data:`django.conf.settings`.

As a consequence, you cannot embed a Django application into another Django
application, nor embed two or more Django applications into a non-Django
application. **The only thing you can do is embed a single Django application
into a non-Django application**.

If you need to embed a Django application into a non-Django application, you
can load it as usual::

    from paste.deploy import loadapp
    
    django_app = loadapp("config:/path/to/config.ini")

or, if you don't use the application factory::

    import os
    from twod.wsgi import DjangoApplication
    
    os.environ['DJANGO_SETTINGS_MODULE'] = "yourpackage.settings"
    django_app = DjangoApplication()

And then you'll be able to mount it wherever you want in the other application.
Please refer to the manual of the other framework to learn how to mount/embed
WSGI applications.

If you had a raw WSGI application (i.e., not using a framework), you could do
something like::

    def raw_wsgi_app(environ, start_response):
        """
        Mount the Django application at "/django" and do something else if the
        requested path is another one.
        
        """
        
        if environ['PATH_INFO'].startswith("/django"):
            # Setting the right paths by moving "/django" to the script name:
            environ['SCRIPT_NAME'] = environ['SCRIPT_NAME'] + "/django"
            environ['PATH_INFO'] = environ['PATH_INFO'][7:]
            return django_app(environ, start_response)
        
        # Do something else if the Django application is not the one requested...

