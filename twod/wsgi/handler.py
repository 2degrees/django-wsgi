# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010-2015, 2degrees Limited.
# All Rights Reserved.
#
# This file is part of twod.wsgi <https://github.com/2degrees/twod.wsgi/>,
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
from django.core.handlers.wsgi import WSGIHandler
from django.core.handlers.wsgi import WSGIRequest as DjangoRequest
from webob import Request as WebobRequest


__all__ = ("TwodWSGIRequest", "DjangoApplication")


class TwodWSGIRequest(DjangoRequest):
    """
    Pythonic proxy for the WSGI environment.
    
    This class is the Django request extended by WebOb's request. Where they
    both have the same members, Django's take precedence. For example, ``.GET``
    uses :attr:`django.core.handlers.wsgi.WSGIRequest.GET` instead of
    :attr:`webob.Request.GET`.
    
    To access WebOb's GET and POST dictionaries, you have to use ``.uGET``
    and ``.uPOST`` respectively.
    
    """

    def __init__(self, environ):
        webob_request = WebobRequest(environ)
        webob_request.make_body_seekable()
        super(TwodWSGIRequest, self).__init__(webob_request.environ)
        self.webob = webob_request

    # django.core.handlers.wsgi.WSGIRequest
    def read(self, *args, **kwargs):
        # Make environ['wsgi.input'] readable by Django, if WebOb read it
        self._stream.stream.seek(0)

        try:
            return super(TwodWSGIRequest, self).read()
        finally:
            # Make environ['wsgi.input'] readable by WebOb
            self._stream.stream.seek(0)


class DjangoApplication(WSGIHandler):
    """
    Django request handler which uses our enhanced WSGI request class.
    
    """

    request_class = TwodWSGIRequest
