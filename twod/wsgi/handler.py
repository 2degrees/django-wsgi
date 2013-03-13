# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010, 2013, 2degrees Limited.
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
from django.core.handlers.wsgi import WSGIRequest, WSGIHandler
from webob import Request


__all__ = ("TwodWSGIRequest", "DjangoApplication")


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
        if self.environ['REQUEST_METHOD'] in ("POST", "PUT", "PATCH"):
            self.environ['wsgi.input'].seek(0)
    
    #}


class DjangoApplication(WSGIHandler):
    """
    Django request handler which uses our enhanced WSGI request class.
    
    """
    request_class = TwodWSGIRequest
