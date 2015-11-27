##############################################################################
#
# Copyright (c) 2010-2015, 2degrees Limited.
# All Rights Reserved.
#
# This file is part of django-wsgi <https://github.com/2degrees/django-wsgi/>,
# which is subject to the provisions of the BSD at
# <http://dev.2degreesnetwork.com/p/2degrees-license.html>. A copy of the
# license should accompany this distribution. THIS SOFTWARE IS PROVIDED "AS IS"
# AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
# INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Django request/response handling a la WSGI.

"""
from django.core.handlers.wsgi import WSGIHandler as DjangoWSGIHandler
from django.core.handlers.wsgi import WSGIRequest as DjangoRequest
from webob import Request as WebobRequest


__all__ = ("DjangoWSGIRequest", "DjangoApplication")


class DjangoWSGIRequest(DjangoRequest):
    """
    Django request that makes an alternative WebOb request available as an
    instance attribute.

    .. attribute:: webob

        :class:`webob.Request` instance for the WSGI environment behind the
        current Django request.
    
    """

    def __init__(self, environ):
        webob_request = WebobRequest(environ)
        webob_request.make_body_seekable()
        super(DjangoWSGIRequest, self).__init__(webob_request.environ)
        self.webob = webob_request

    def read(self, *args, **kwargs):
        # Make environ['wsgi.input'] readable by Django, if WebOb read it
        self._stream.stream.seek(0)

        try:
            return super(DjangoWSGIRequest, self).read()
        finally:
            # Make environ['wsgi.input'] readable by WebOb
            self._stream.stream.seek(0)


class DjangoApplication(DjangoWSGIHandler):
    """
    Django request handler which uses our enhanced WSGI request class.
    
    """

    request_class = DjangoWSGIRequest


APPLICATION = DjangoApplication()
"""WSGI application based on :class:`DjangoApplication`."""
