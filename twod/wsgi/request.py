# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010, 2degrees Limited <gustavonarea@2degreesnetwork.com>.
# All Rights Reserved.
#
# This file is part of twod.wsgi <http://bitbucket.org/Gustavo/twod.wsgi/>.
#
# twod.wsgi is subject to the provisions of the MIT/X license at
# <http://www.opensource.org/licenses/mit-license.php>.  A copy of the license
# should accompany this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY
# AND ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
# INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Django request handling a la WSGI.

"""
from webob import Request
from django.core.handlers.wsgi import WSGIRequest, WSGIHandler


class TwodWSGIRequest(WSGIRequest, Request):
    """
    Pythonic proxy for the WSGI environment.
    
    This class is the Django request extended by WebOb's request. Where they
    both have the same members, Django's take precedence. For example, ``.GET``
    uses :attr:`django.core.handlers.wsgi.WSGIRequest.GET` instead of
    :attr:`webob.Request.GET`.
    
    To access WebOb's GET and POST dictionaries, you have to use ``.unicode_GET``
    and ``.unicode_POST`` respectively.
    
    """
    
    def __init__(self, environ):
        Request.__init__(self, environ)
        WSGIRequest.__init__(self, environ)
    
    #{ Attribute handing
    
    __getattr__ = Request.__getattr__
    __delattr__ = Request.__delattr__
    
    def __setattr__(self, attr, value):
        self.environ.setdefault("webob.adhoc_attrs", {})[attr] = value
    
    #{ Handing arguments
    
    unicode_POST = Request.POST
    unicode_GET = Request.GET
    
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


class TwodWSGIHandler(WSGIHandler):
    """
    Django request handler which uses our enhanced request class.
    
    """
    request_class = TwodWSGIRequest
