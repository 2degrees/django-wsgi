# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010, 2degrees Limited <gustavonarea@2degreesnetwork.com>.
# All Rights Reserved.
#
# This file is part of twod.wsgi <http://bitbucket.org/2degrees/twod.wsgi/>,
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
from webob import Request
from django.core.handlers.wsgi import WSGIRequest, WSGIHandler
from django.http import HttpResponse

__all__ = ("TwodWSGIRequest", "TwodResponse", "DjangoApplication")


_ACTUAL_REASON_HEADER = "X-Actual-Status-Reason"


class TwodWSGIRequest(WSGIRequest, Request):
    """
    Pythonic proxy for the WSGI environment.
    
    This class is the Django request extended by WebOb's request. Where they
    both have the same members, Django's take precedence. For example, ``.GET``
    uses :attr:`django.core.handlers.wsgi.WSGIRequest.GET` instead of
    :attr:`webob.Request.GET`.
    
    To access WebOb's GET and POST dictionaries, you have to use ``.uGET``
    and ``.uPOST`` respectively.
    
    """
    
    # The following are used as attributes by Django's request class instances.
    # If we don't set them class-wide, WebOb is going to put them into its
    # ``webob.adhoc_attrs`` variable. See webob.Request:__setattr__.
    environ = None
    path = None
    method = None
    META = None
    
    def __init__(self, environ):
        Request.__init__(self, environ)
        WSGIRequest.__init__(self, environ)
    
    #{ Handing arguments
    
    uPOST = Request.POST
    uGET = Request.GET
    
    # webob.Request
    @property
    def str_POST(self):
        """
        Return the POST arguments by using WebOb.
        
        """
        # Before returning the POST arguments, we have to restore the content
        # length, which is reset by WebOb:
        original_content_length = self.environ.get("CONTENT_LENGTH")
        try:
            return super(TwodWSGIRequest, self).str_POST
        finally:
            self.environ['CONTENT_LENGTH'] = original_content_length
            # "Resetting" the input so Django will read it:
            self._seek_input()
    
    # django.core.handlers.wsgi.WSGIRequest
    def _load_post_and_files(self):
        """
        Parse the POST arguments and uploaded files by using Django.
        
        """
        try:
            return super(TwodWSGIRequest, self)._load_post_and_files()
        finally:
            # "Resetting" the input so WebOb will read it:
            self._seek_input()
    
    def _seek_input(self):
        if "wsgi.input" in self.environ:
            self.environ['wsgi.input'].seek(0)
    
    #}


class TwodResponse(HttpResponse):
    """
    Django-based response class which keeps the HTTP status reason phrase.
    
    The original implementation in Django simply keeps the status code and
    does not allow developers to use custom HTTP status reason phrase, which
    is explicitly allowed by the HTTP specification:
    http://www.w3.org/Protocols/rfc2616/rfc2616-sec6.html
    
    """
    
    def __init__(self, content="", mimetype=None, status=None, *args, **kwargs):
        if isinstance(status, basestring):
            # The status is given as a real HTTP status header, so we should
            # tell the code and the reason apart for Django:
            (status_code, status_reason) = status.split(" ", 1)
            status_code = int(status_code)
            self.status_reason = status_reason or None
        else:
            # The status has been given the old way supported by Django, simply
            # the status code as an integer:
            status_code = status
            self.status_reason = None
        
        super(TwodResponse, self).__init__(content, mimetype, status_code,
                                           *args, **kwargs)
        
        # Including the actual reason header if necessary:
        if self.status_reason:
            reason_header = "%s %s" % (self.status_code, self.status_reason)
            self._headers[_ACTUAL_REASON_HEADER.lower()] = \
                (_ACTUAL_REASON_HEADER, reason_header)


class DjangoApplication(WSGIHandler):
    """
    Django request handler which uses our enhanced WSGI request class.
    
    """
    request_class = TwodWSGIRequest
    
    def __call__(self, environ, start_response):
        start_response_wrapper = _StartResponseWrapper(start_response)
        return super(DjangoApplication, self).__call__(environ,
                                                       start_response_wrapper)


#{ Internals


class _StartResponseWrapper(object):
    """
    Wrapper for an actual start_response() callable which replaces the
    ``status`` with the actual status reason, if any.
    
    We need to iterate over all the ``response_headers`` until we find the
    actual status reason. If it's not there, we'd have wasted time and
    resources, but there's no other way around this until Django fixes the bug:
    http://code.djangoproject.com/ticket/12747
    
    """
    
    def __init__(self, original_start_response):
        self.original_start_response = original_start_response
    
    def __call__(self, status, response_headers, exc_info=None):
        final_headers = []
        
        for (header_name, header_value) in response_headers:
            if header_name == _ACTUAL_REASON_HEADER:
                status = header_value
            else:
                final_headers.append((header_name, header_value))
        
        return self.original_start_response(status, final_headers)


#}
