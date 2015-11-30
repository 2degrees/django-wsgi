========
Releases
========

Version 1 Beta 1 (2015-11-30)
=============================

This is a backwards-incompatible fork of `twod.wsgi v1.0.1
<http://pythonhosted.org/twod.wsgi/>`_.

The most significant change is that the configuration-related functionality has
been split away from **django-wsgi**, as it is not strictly to do with improving
Django-WSGI interoperability. This functionality is now available in the project
`django-pastedeploy-settings
<http://pythonhosted.org/django-pastedeploy-settings/>`_.

Additionally, the following changes were made:

* :class:`twod.wsgi.handler:TwodWSGIRequest` was renamed to
  :class:`django_wsgi.handler:DjangoWSGIRequest`, and
  :class:`twod.wsgi.exc:TwodWSGIException` was renamed to
  :class:`django_wsgi.exc:DjangoWSGIException`.
* :class:`django_wsgi.handler:DjangoWSGIRequest` is no longer subclassing both
  Django's and WebOb's requests. Django's request class is the only parent now,
  and the WebOb request instance is available as the instance attribute
  ``webob`` (i.e., ``request.webob``).
* Introduced :data:`django_wsgi.handler.APPLICATION` to make it possible to
  set our handler directly via the ``WSGI_APPLICATION`` setting.
* Removed the class ``TwodResponse``, which supported the setting of custom
  HTTP status reasons, since newer versions of Django now support this.
* Removed ability to import directly from the package :mod:`django_wsgi`.
* Seek operations have been restricted to the ``wsgi.input`` of POST and PUT
  requests. This fixes a bug with Django Admin in Django 1.2 where a view
  gets the POST arguments even if the request is a GET one.
* Added Django 1.6 compatibility.
* Added Python 3 compatibility.
