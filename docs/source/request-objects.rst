===============================
WebOb request objects in Django
===============================

*django-wsgi* extends Django's WSGI handler
(:class:`django.core.handlers.wsgi.WSGIHandler`) and the
:class:`~django.http.HttpRequest` class, so that our handler can use our
extended request class.

As mentioned before, what Django calls "handler" is actually a generic WSGI
application that wraps your Django project. We'll stick to "WSGI application"
from now on.

This extended WSGI application offers a better compatibility with WSGI
middleware and applications thanks to the integration with
:class:`webob.Request`. `WebOb <http://docs.webob.org/en/latest/>`_ is another
offers pythonic APIs to WSGI requests (the so-called "WSGI environment") and
responses -- much like :class:`~django.http.HttpRequest` and
:class:`~django.http.HttpResponse`, but better:

- Django copies some values from the environment into its own request object,
  on every request, no matter if you are going to use them or not.
- When you edit a WebOb request, no matter what you do, your changes will be
  applied in the actual WSGI environment. This is key to interoperability.
- WebOb covers the environment comprehensively, with getters and other methods
  to make it easier and more fun to handle.
- Django refuses to read POST requests if the ``CONTENT_LENGTH`` equals ``"-1"``
  (may happen when read by WSGI middleware), while the intended behaviour
  is to **force** wrappers to read it.

Instances of :class:`our request <django_wsgi.handler.DjangoWSGIRequest>` make
an the equivalent WebOb request available as an attribute, so that you can use
WebOb's accessors in your code. For example::

    def my_view(request):
        if 'MSIE' in request.webob.user_agent:
            response = HttpResponseNotFound()
        else:
            response = HttpResponse()
        return response

This request class will be used instead of the built-in one when you configure
Django to use our "handler" in your ``settings.py``::

    WSGI_APPLICATION = 'django_wsgi.handler.APPLICATION'

See the `documentation for webob.Request
<http://docs.webob.org/en/latest/reference.html#request>`_ to learn more about
the new features you now have at your disposal.


Using the WSGI application directly
-----------------------------------

You can import it as you would normally do in Django::

    from os import environ
    environ['DJANGO_SETTINGS_MODULE'] = "yourpackage.settings"
    
    from django_wsgi.handler import DjangoApplication
