========
Releases
========

Version 1.0 Alpha 4 (unreleased)
================================

* Added :func:`twod.wsgi.factories.add_media_to_app`, which receives a Django
  powered WSGI application and returns a WSGI application which serves the
  entire Web site (including the media).


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
