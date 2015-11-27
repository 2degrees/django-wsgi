========
Releases
========

Version 1 Beta 1 (unreleased)
=============================

This is a backwards-incompatible fork of `twod.wsgi v1.0.1
<http://pythonhosted.org/twod.wsgi/>`_.

The most significant change is that the configuration-related functionality has
been split away from **django-wsgi**, as it is not strictly to do with improving
Django-WSGI interoperability. This functionality is now available in the project
`django-pastedeploy-settings
<http://pythonhosted.org/django-pastedeploy-settings/>`_.

Additionally, the following changes were made:

* The following elements of the public API where moved and/or renamed:
  - :mod:`twod.wsgi` to :mod:`django_wsgi`.
  - :class:`twod.wsgi.handler:TwodWSGIRequest` to
    :class:`django_wsgi.handler:DjangoWSGIRequest`.
  - :class:`twod.wsgi.exc:TwodWSGIException` to
    :class:`django_wsgi.exc:DjangoWSGIException`.
* Removed the class ``TwodResponse``, which supported the setting of custom
  HTTP status reasons, since newer versions of Django now support this.
* Removed ability to import directly from the package :mod:`django_wsgi`.
* Seek operations have been restricted to the ``wsgi.input`` of POST and PUT
  requests. This fixes a bug with Django Admin in Django 1.2 where a view
  gets the POST arguments even if the request is a GET one.
* Added Django 1.6 compatibility.
* Added Python 3 compatibility.
