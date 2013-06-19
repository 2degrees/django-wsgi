:mod:`twod.wsgi`: WSGI as first-class citizen in Django applications
====================================================================

:Sponsored by: `2degrees Limited <http://dev.2degreesnetwork.com/>`_.
:Latest release: |release|

**twod.wsgi** allows you to use the advanced/common functionality in WSGI that
Django projects don't get out-of-the-box, by improving the interoperability
between Django and the rest of the WSGI ecosystem. To accomplish this,
this library provides the following:

- An enhanced :class:`~django.http.HttpRequest` class extended by the
  fully-featured :class:`webob.Request` (which is absolutely backwards
  compatible).
- Functions to run WSGI applications inside Django reliably.
- A Django middleware which implements the `wsgiorg.routing_args
  <http://wsgi.org/wsgi/Specifications/routing_args>`_ standard.

By improving Django's interoperability, you gain the ability to rapidly
integrate many third party software with Django, or simply use a component
which you think outperforms Django's current implementation.

Finally, it's worth mentioning that:

- This library has been used in production systems since 2009.
- This project is comprehensively tested and fully documented.
- It is known to work with Django 1.1.1-1.4.5 and Python 2.5-2.7.
  Please let us know if it doesn't.


Contents
========

.. toctree::
   :maxdepth: 2
   
   request-objects
   embedded-apps
   routing-args
   api
   about
   changelog
