:mod:`django_wsgi`: WSGI as first-class citizen in Django applications
======================================================================

:Sponsored by: `2degrees Limited <http://dev.2degreesnetwork.com/>`_.
:Latest release: |release|

**django-wsgi** allows you to use the advanced/common functionality in WSGI that
Django projects don't get out-of-the-box, by improving the interoperability
between Django and the rest of the WSGI ecosystem. To accomplish this,
this library provides the following:

- The ability to use the fully-featured ``Request`` class from WebOb along side
  Django's :class:`~django.http.HttpRequest`.
- Functions to run WSGI applications inside Django reliably.
- A Django middleware which implements the `wsgiorg.routing_args
  <http://wsgi.org/wsgi/Specifications/routing_args>`_ standard.

By improving Django's interoperability, you gain the ability to rapidly
integrate many third party software with Django, or simply use a component
which you think outperforms Django's current implementation.

Finally, it's worth mentioning that:

- This library has been used in production systems since 2009.
- This project is comprehensively tested and fully documented.
- It supports Django v1.6+, CPython 2.7, CPython 3.3+, PyPy and PyPy 3.


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
