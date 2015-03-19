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
Tests for the WSGI request handler.

"""
from StringIO import StringIO
from urllib import urlencode

from django.core.handlers.wsgi import WSGIRequest
from nose.tools import eq_, ok_, assert_false, assert_not_equal
from webob import Request

from twod.wsgi.handler import DjangoApplication, TwodWSGIRequest

from tests import BaseDjangoTestCase, complete_environ


class TestRequest(BaseDjangoTestCase):
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
        environ = complete_environ(**environ)
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
        environ = complete_environ(QUERY_STRING=qs)
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
        environ = complete_environ(**environ)
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

    def test_body_seeking(self):
        """
        A seek to zero is performed on the "wsgi.input" in POST and PUT requests
        only.
        
        HEAD and GET requests don't have body, but the "wsgi.input" object may
        have been set -- In such situation, no seek must be performed.
        
        """
        body = StringIO(urlencode({'foo': "bar", 'bar': "foo"}))

        head_request = TwodWSGIRequest({
            'REQUEST_METHOD': "HEAD",
            'PATH_INFO': "/",
            'wsgi.input': body,
            })

        get_request = TwodWSGIRequest({
            'REQUEST_METHOD': "GET",
            'PATH_INFO': "/",
            'wsgi.input': body,
            })

        post_request = TwodWSGIRequest({
            'REQUEST_METHOD': "POST",
            'PATH_INFO': "/",
            'CONTENT_TYPE': "application/x-www-form-urlencoded",
            'wsgi.input': body,
            })

        put_request = TwodWSGIRequest({
            'REQUEST_METHOD': "PUT",
            'PATH_INFO': "/",
            'CONTENT_TYPE': "application/x-www-form-urlencoded",
            'wsgi.input': body,
            })

        patch_request = TwodWSGIRequest({
            'REQUEST_METHOD': "PATCH",
            'PATH_INFO': "/",
            'CONTENT_TYPE': "application/x-www-form-urlencoded",
            'wsgi.input': body,
            })

        # Requests where seeks must NOT be performed:
        for request in (head_request, get_request):
            body.seek(3)
            request._seek_input()
            eq_(body.tell(), 3, "%s requests have no body" % request.method)

        # Requests where seeks MUST be performed:
        for request in (post_request, put_request, patch_request):
            body.seek(3)
            request._seek_input()
            eq_(body.tell(), 0, "%s requests have body" % request.method)

    def _make_requests(self, environ):
        base_environ = complete_environ(**environ)

        requests = (WSGIRequest(base_environ.copy()),
                    Request(base_environ.copy()),
                    TwodWSGIRequest(base_environ.copy()))

        wsgi_input_body = environ['wsgi.input'].read()
        for request in requests:
            request.environ['wsgi.input'] = StringIO(wsgi_input_body)

        return requests

    #{ Testing WebOb ad-hoc attributes

    def test_getting_attributes(self):
        environ = {'webob.adhoc_attrs': {'foo': "bar"}}
        environ = complete_environ(**environ)
        req = TwodWSGIRequest(environ)
        ok_(hasattr(req, "foo"))
        eq_(req.foo, "bar")

    def test_setting_attributes(self):
        req = TwodWSGIRequest(complete_environ())
        req.foo = "bar"
        ok_(hasattr(req, "foo"))
        eq_(req.foo, "bar")

        # Ensure it's also in the WebOb ad-hoc attributes dict
        ok_("webob.adhoc_attrs" in req.environ)
        ok_("foo" in req.environ['webob.adhoc_attrs'])

    def test_deleting_attributes(self):
        environ = {'webob.adhoc_attrs': {'foo': "bar"}}
        environ = complete_environ(**environ)
        req = TwodWSGIRequest(environ)
        del req.foo
        assert_false(hasattr(req, "foo"))

    #}


class TestWSGIHandler(BaseDjangoTestCase):
    """Tests for :class:`DjangoApplication`."""

    def setup(self):
        self.handler = TelltaleHandler()
        super(TestWSGIHandler, self).setup()

    def test_right_request_class(self):
        """The WSGI handler must use Twod's request class."""
        environ = complete_environ(REQUEST_METHOD="GET", PATH_INFO="/")
        def start_response(status, response_headers): pass

        self.handler(environ, start_response)

        ok_(isinstance(self.handler.request, TwodWSGIRequest))


#{ Test utilities


class TelltaleHandler(DjangoApplication):
    """
    Mock WSGI handler based on Twod's, which is going to be called once and it's
    going to store the request object it got.
    
    """

    def get_response(self, request):
        self.request = request
        return super(TelltaleHandler, self).get_response(request)


#}
