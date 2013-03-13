================================
:mod:`twod.wsgi` End-User Manual
================================

Table of contents
=================

.. toctree::
   :maxdepth: 2
   
   request-objects
   embedded-apps
   routing-args


Introduction
============

To date, Django users have not been able to use the full potential of WSGI
in their applications and that also affects the wider Python Web development
community, which could be benefiting from reusable components written by Django
users, who represent an important portion of said community.

In the beginning there was no support at all and nowadays compliance is nearly
complete at the bare minimum level. This has been pointed out many times, by known
members of both WSGI [#django_wsgi]_ and Django [#django_people]_ communities.

WSGI is all about **interoperability** and that leads to **reusability**, in this
sense, reusability beyond `more of the same <http://pinaxproject.com/>`_: From
absolutely independent projects. And `cooperation is the key
<http://compoundthinking.com/blog/index.php/2009/02/04/wsgi-and-cooperation/>`_.

*twod.wsgi*'s aim is to be the "cooperation bridge" between Django and WSGI, until
Django crosses this bridge. It is a very simple library made up of the following
components:

- Functions to run WSGI applications inside Django reliably.
- An :class:`~django.http.HttpRequest` class extended by the fully-featured
  :class:`webob.Request` (which is absolutely backwards compatible).
- A Django middleware which implements the `wsgiorg.routing_args
  <http://wsgi.org/wsgi/Specifications/routing_args>`_ standard.

The author, who is a core developer at some mainstream WSGI projects, believes
these components bring Django to the same level as frameworks like TurboGears, as
far as WSGI support is concerned.

Hopefully after reading this manual you will realize how powerful WSGI can be!
But keep in mind this manual simply describes the way third party software
can be integrated in your application with *twod.wsgi*; you should still check
the official documentation for that third party package.

.. rubric:: Footnotes

.. [#django_wsgi] "`Django developer discovers WSGI...
    <http://compoundthinking.com/blog/index.php/2009/01/21/django-developer-discovers-wsgi/>`_"
    by Mark Ramm.

.. [#django_people] "`WSGI middleware is awesome, and Django should use it more
    <http://www.eflorenzano.com/blog/post/wsgi-middlware-awesome-django-use-it-more/>`_"
    by Eric Florenzano and "`Hot Django on WSGI Action
    <http://alexgaynor.net/2010/jan/11/hot-django-wsgi-action-announcing-django-wsgi/>`_"
    by Alex Gaynor.
