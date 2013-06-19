========
Releases
========

Version 2 Beta 1 (2013-06-19)
=============================

This release is backwards incompatible with v1.

The most significant change is that the configuration-related functionality has
been split away from **twod.wsgi**, as it is not strictly to do with improving
Django-WSGI interoperability. This functionality is now available in the project
`django-pastedeploy-settings
<http://pythonhosted.org/django-pastedeploy-settings/>`_.

Additionally, the following changes were made:

* Removed the class ``TwodResponse``, which supported the setting of custom
  HTTP status reasons, since newer versions of Django now support this.
* Removed ability to import directly from the package :mod:`twod.wsgi`.
* Seek operations have been restricted to the ``wsgi.input`` of POST and PUT
  requests. This fixes a bug with Django Admin in Django 1.2 where a view
  gets the POST arguments even if the request is a GET one.


Version 1.0.1 (2011-06-29)
==========================

Version 1.0.1 adds support for configuration variables which can either be 
``None`` if left empty or strings otherwise. This functionality is useful when
overriding settings in inherited blocks.


Version 1.0 Final (2010-07-22)
==============================

The code is the same as in the release candidate, but the documentation and
the distribution metadata changed as follows:

* Updated the URL to the (new) `mailing list
  <http://groups.google.com/group/2degrees-floss>`_.
* Removed not applicable trove classifier for the Python Package Index.
* Mentioned that settings introduced in Django 1.2 are not yet supported by
  the Paste Deploy application factory.


Version 1.0 RC 1 (2010-04-26)
=============================

The fourth alpha proved to very stable as no bugs were found, so it's being
released as is, as a Release Candidate with one minor modification: 

* Corrected URL to 2degrees license in the docstrings.


Version 1.0 Alpha 4 (2010-03-29)
================================

* Added :func:`twod.wsgi.factories.add_media_to_app`, which receives a Django
  powered WSGI application and returns a WSGI application which serves the
  entire Web site (including the media).
* Fixed typos in the documentation: The ``django_settings_module`` option in
  ``paste-factory`` was being put in the ``[DEFAULT]`` section;
  the right location is an application section.
* Paste itself was not a requirement in :file:`setup.py`, people who didn't
  have it installed already would get :class:`ImportError` exceptions.


Version 1.0 Alpha 3 (2010-03-11)
================================

Fixed another packaging problem: :file:`ez_setup.py` was not included in the
final distribution. This time it was certainly our fault.


Version 1.0 Alpha 2 (2010-03-08)
================================

Fixed embarrassing and inexplicable packaging problem caused by setuptools
(the :file:`VERSION.txt` file was supposed to be included in the distribution
but it wasn't).


Version 1.0 Alpha 1 (2010-03-08)
================================

Initial release. Comprehensively tested and documented.
