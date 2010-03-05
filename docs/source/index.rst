:mod:`twod.wsgi`: WSGI as first-class citizen in Django applications
====================================================================

:Sponsored by: `2degrees Limited <http://dev.2degreesnetwork.com/>`_.
:Latest release: |release|


**twod.wsgi** unlocks Django applications so developers can take advantage of
the `wealth of existing WSGI software
<http://pypi.python.org/pypi?%3Aaction=search&term=wsgi>`_, as the other
popular Python frameworks do. It won't break you existing Django applications because
it's 100% compatible with Django and you can start using the functionality
offered by this library progressively. It should be really easy to get started,
particularly for developers who are familiar with frameworks like Pylons or
TurboGears.

Among many other things, one of the components alone provides `solutions to
some enterprise requirements for Django
<http://groups.google.com/group/django-developers/browse_thread/thread/c89e028a536514d3>`_:

- It's now possible to run code at startup time, in an straightforward yet
  extremely flexible fashion, which will also work on development servers if you
  want it to -- not only when deployed on a production server.
- You can now stop using a Python module to store your application settings, in
  order to use an intuitive and widely used mechanism that scales up and scales
  down. It will just work and you won't have to update any other file in your
  application.
- It's finally possible to run WSGI middleware in development servers, the same
  way you may do it on production servers.

And this is just the tip of the iceberg. By improving Django's interoperability,
you gain the ability to rapidly integrate many third party software with Django,
or simply use a component which you think outperforms Django's current
implementation.

Finally, it's worth mentioning that:

- This project is comprehensively tested and fully documented.
- Most of the functionality has been in heavy use for over 4 months before the
  initial alpha release, as `a patched version of Django
  <http://groups.google.com/group/django-developers/browse_thread/thread/08c7ffeee7b9343c>`_.
- Our long-term goal is to see these improvements in Django itself -- Either with
  our implementation or someone else's. Before deciding to start an independent
  project, we had already offered our help to people within the Django community
  working towards similar aims and the offer still stands.
- It is known to work with Django 1.1.1 and Python 2.5, and we expect it to
  work with Django 1.1-1.2 and Python 2.4-2.6 too -- Please let us know if it
  doesn't.


Contents
========

.. toctree::
   :maxdepth: 2
   
   manual/index
   api
   about
   changelog
