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
Tests for the WSGI request handler.

"""
from StringIO import StringIO
from urllib import urlencode

from nose.tools import eq_, ok_, assert_false, assert_not_equal
from webob import Request
from django.core.handlers.wsgi import WSGIRequest, WSGIHandler

from twod.wsgi.request import TwodWSGIRequest, TwodWSGIHandler


class TestRequest(object):
    """Tests for the enhanced request objects."""
    
    #{ Testing GET and POST arguments
    
    def test_post(self):
        """
        POST arguments must be handled by Django.
        
        Also make sure both Django and WebOb can read the input (i.e., POST
        variables and files uploaded).
        
        """
        input = urlencode({'foo': "bar", 'bar': "foo"})
        input_length = str(len(input))
        environ = {
            'REQUEST_METHOD': "POST",
            'CONTENT_TYPE': "application/x-www-form-urlencoded",
            'CONTENT_LENGTH': input_length,
            'wsgi.input': StringIO(input),
            }
        (django_req, webob_req, twod_req) = self._make_requests(environ)
        
        eq_(twod_req.POST, django_req.POST)
        assert_not_equal(twod_req.POST, webob_req.POST)
        # Although WebOB POST arguments are still accessible and read, even
        # though Django read them first:
        eq_(twod_req.uPOST, webob_req.POST)
        
        # WebOb shouldn't have changed the CONTENT_LENGTH, otherwise Django
        # won't read the input:
        eq_(twod_req.environ['CONTENT_LENGTH'], input_length)
        
        # Finally, let's make sure Django will read the input even if WebOb read
        # it first:
        (django_req2, webob_req2, twod_req2) = self._make_requests(environ)
        eq_(twod_req2.uPOST, webob_req2.POST)
        eq_(twod_req2.POST, django_req2.POST)
    
    def test_get(self):
        """
        GET arguments must be handled by Django.
        
        """
        qs = urlencode({'foo': "bar", 'bar': "foo"})
        environ = {
            'QUERY_STRING': qs,
            }
        (django_req, webob_req, twod_req) = self._make_requests(environ)
        
        eq_(twod_req.GET, django_req.GET)
        assert_not_equal(twod_req.GET, webob_req.GET)
        # Although WebOB GET arguments are still accessible and read, even
        # though Django read them first:
        eq_(twod_req.uGET, webob_req.GET)
        
        # Finally, let's make sure Django will read the QS even if WebOb read
        # it first:
        (django_req2, webob_req2, twod_req2) = self._make_requests(environ)
        eq_(twod_req2.uGET, webob_req2.GET)
        eq_(twod_req2.GET, django_req2.GET)
    
    def test_content_length_in_post(self):
        """
        The content length should be set if it wasn't set originally in a
        POST request.
        
        """
        environ = {
            'REQUEST_METHOD': "POST",
            'CONTENT_TYPE': "application/x-www-form-urlencoded",
            'wsgi.input': StringIO(urlencode({'foo': "bar", 'bar': "foo"})),
            }
        twod_request = TwodWSGIRequest(environ)
        
        ok_("CONTENT_LENGTH" not in twod_request.environ,
            "The Content-Length was set in the constructor")
        
        # The CONTENT_LENGTH shouldn't have been set after reading the POST
        # arguments with Django:
        twod_request.POST
        ok_("CONTENT_LENGTH" not in twod_request.environ)
        
        # But it should have been set when read with WebOb:
        twod_request.uPOST
        ok_("CONTENT_LENGTH" in twod_request.environ)
    
    def _make_requests(self, environ):
        
        base_environ = {
            'REQUEST_METHOD': "GET",
            }
        base_environ.update(environ)
        
        requests = (WSGIRequest(base_environ.copy()),
                    Request(base_environ.copy()),
                    TwodWSGIRequest(base_environ.copy()))
        
        if "wsgi.input" in environ:
            old_input = environ['wsgi.input']
            for request in requests:
                request.environ['wsgi.input'] = StringIO(old_input.read())
                old_input.seek(0)
        
        return requests
    
    #{ Testing WebOb ad-hoc attributes
    
    def test_getting_attributes(self):
        environ = {
            'REQUEST_METHOD': "GET",
            'webob.adhoc_attrs': {'foo': "bar"},
            }
        req = TwodWSGIRequest(environ)
        ok_(hasattr(req, "foo"))
        eq_(req.foo, "bar")
    
    def test_setting_attributes(self):
        environ = {
            'REQUEST_METHOD': "GET",
            }
        req = TwodWSGIRequest(environ)
        req.foo = "bar"
        ok_(hasattr(req, "foo"))
        eq_(req.foo, "bar")
    
    def test_deleting_attributes(self):
        environ = {
            'REQUEST_METHOD': "GET",
            'webob.adhoc_attrs': {'foo': "bar"},
            }
        req = TwodWSGIRequest(environ)
        del req.foo
        assert_false(hasattr(req, "foo"))
    
    #}

