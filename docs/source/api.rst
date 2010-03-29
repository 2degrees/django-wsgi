======================================
API documentation for :mod:`twod.wsgi`
======================================

.. automodule:: twod.wsgi
    :synopsis: Enhanced WSGI support for Django
    :members: DjangoApplication, TwodResponse
    :show-inheritance:


.. autoclass:: twod.wsgi.handler.TwodWSGIRequest
    :show-inheritance:

Embedded applications
=====================

.. autofunction:: make_wsgi_view

.. autofunction:: call_wsgi_app


Media serving
=============

.. autofunction:: twod.wsgi.factories.add_media_to_app


Exceptions
==========

.. automodule:: twod.wsgi.exc
    :synopsis: Exceptions ever raised by twod.wsgi
    :members:
    :show-inheritance:


