======================================
:mod:`webob.Request` objects in Django
======================================

*twod.wsgi* extends Django's WSGI handler
(:class:`django.core.handlers.wsgi.WSGIHandler`) and the
:class:`~django.http.HttpRequest` class, so our handler uses our extended
request class. This handler is used when you use the :doc:`paste-factory`, but
you can still use the handler without it.

As mentioned before, what Django calls "handler" is actually a generic WSGI
application that wraps your Django project. We'll stick to "WSGI application"
from now on.

This extended WSGI application offers a better WSGI support, as you would expect,
because the request class it uses borrows functionality from
:class:`webob.Request`. `WebOb <http://pythonpaste.org/webob/>`_ is another
popular component of the Paste project, which offers pythonic APIs to WSGI
requests (the so-called "WSGI environment") and responses, like
:class:`~django.http.HttpRequest` and :class:`~django.http.HttpResponse`,
but better:

- Django copies some values from the environment into its own request object,
  on every request, no matter if you are going to use them or not.
- When you edit a WebOb request, no matter what you do, your changes will be
  applied in the actual WSGI environment. This is key to interoperability.
- WebOb covers the environment comprehensively, with getters and other methods
  to make it easier and more fun to handle.
- Django refuses to read POST requests if the ``CONTENT_LENGTH`` equals ``"-1"``
  (may happen when read by WSGI middleware), while the intended behaviour
  is to **force** wrappers to read it.

:class:`Our new request class <twod.wsgi.handler.TwodWSGIRequest>` extends both
:class:`~django.http.HttpRequest` and :class:`webob.Request`, and because the
members of the former take precedence over the latter, it's 100%
compatible with the built-in request class in Django. :class:`webob.Response` is
not used in *twod.wsgi*.

:class:`~django.http.HttpRequest` takes precedence even with the following
name clashes with :class:`webob.Request`:

- ``environ``. 
- ``path``.
- ``method``.
- ``POST``.
- ``GET``.

:class:`webob.Request`'s ``.POST`` and ``.GET`` are available as ``.uPOST`` and
``.uGET``, respectively. The other attributes are equivalent in both classes.

When you use this application, your views receive the request as an instance of
:class:`~twod.wsgi.handler.TwodWSGIRequest` automatically.

See the `API documentation for webob.Request
<http://pythonpaste.org/webob/class-webob.Request.html>`_ to meet the new
members of your request objects.


Using the WSGI application directly
-----------------------------------

If you're not using the :doc:`paste-factory`, you can import it as you would
normally do in Django::

    from os import environ
    environ['DJANGO_SETTINGS_MODULE'] = "yourpackage.settings"
    
    from twod.wsgi import DjangoApplication

If you do use the application factory, but still need to create an instance of
the generic WSGI application for your Django project (e.g., for testing
purposes), you could just do::

    from twod.wsgi import DjangoApplication

