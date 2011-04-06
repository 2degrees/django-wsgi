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
Tests for the WSGI request handler.

"""
from StringIO import StringIO
from urllib import urlencode

from nose.tools import eq_, ok_, assert_false, assert_not_equal
from webob import Request
from django.core.handlers.wsgi import WSGIRequest

from twod.wsgi import DjangoApplication
from twod.wsgi.handler import (TwodWSGIRequest, TwodResponse,
                               _StartResponseWrapper)

from tests import BaseDjangoTestCase, MockStartResponse, complete_environ


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
        
        # Requests where seeks must NOT be performed:
        for request in (head_request, get_request):
            body.seek(3)
            request._seek_input()
            eq_(body.tell(), 3, "%s requests have no body" % request.method)
        
        # Requests where seeks MUST be performed:
        for request in (post_request, put_request):
            body.seek(3)
            request._seek_input()
            eq_(body.tell(), 0, "%s requests have body" % request.method)
    
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
        # Making sure they're in the WebOb ad-hoc attributes dict, with nothing
        # else:
        ok_("webob.adhoc_attrs" in req.environ)
        eq_(len(req.environ['webob.adhoc_attrs']), 1,
            "WebOb.Request has the following ad-hoc attributes: %s" %
            req.environ['webob.adhoc_attrs'])
        ok_("foo" in req.environ['webob.adhoc_attrs'])
    
    def test_deleting_attributes(self):
        environ = {
            'REQUEST_METHOD': "GET",
            'webob.adhoc_attrs': {'foo': "bar"},
            }
        req = TwodWSGIRequest(environ)
        del req.foo
        assert_false(hasattr(req, "foo"))
    
    #}


class TestResponse(BaseDjangoTestCase):
    """Tests for :class:`TwodResponse`."""
    
    def test_status_phrase_is_kept(self):
        """
        Unlike Django's, 2degrees' Response objects must kept the status phrase.
        
        """
        body = "this is the body"
        status = "200 Everything's gonna be alright"
        response = TwodResponse(body, status=status)
        # The original status code should remain integer:
        eq_(response.status_code, 200)
        # But the reason phrase must still be available:
        eq_(response.status_reason, status[4:])
        # And both must be included in the actual response:
        expected_response = (
            "Content-Type: text/html; charset=utf-8\n"
            "X-Actual-Status-Reason: %s\n"
            "\n"
            "%s"
            ) % (status, body)
        eq_(expected_response, str(response))
    
    def test_backwards_compatibility(self):
        """
        The response must behave like Django's unless explicitly told otherwise.
        
        """
        body = "this is the body"
        status = 200
        response = TwodResponse(body, status=status)
        # The original status code should remain integer:
        eq_(response.status_code, 200)
        # But the reason phrase must still be available:
        eq_(response.status_reason, None)
        # And both must be included in the actual response:
        expected_response = (
            "Content-Type: text/html; charset=utf-8\n"
            "\n"
            "%s"
            ) % body
        eq_(expected_response, str(response))
    
    def test_status_reason_is_taken_when_available(self):
        """
        The status reason phrase must be taken when it's really set.
        
        """
        body = "this is the body"
        # Testing a status code as string, but which doesn't have a reason:
        status1 = "200 "
        response1 = TwodResponse(body, status=status1)
        eq_(response1.status_code, 200)
        eq_(response1.status_reason, None)
        # Testing a status code as string which has a reason:
        status2 = "200 That is right"
        response2 = TwodResponse(body, status=status2)
        eq_(response2.status_code, 200)
        eq_(response2.status_reason, status2[4:])


class TestWSGIHandler(BaseDjangoTestCase):
    """Tests for :class:`DjangoApplication`."""
    
    def setup(self):
        self.handler = TelltaleHandler()
        super(TestWSGIHandler, self).setup()
    
    def test_right_request_class(self):
        """The WSGI handler must use Twod's request class."""
        environ = {'REQUEST_METHOD': "GET"}
        def start_response(status, response_headers): pass
        
        # We're going to get an exception because not all the environment keys
        # are defined, but that doesn't matter because by that time we should
        # already have the request object and that's all we need:
        try:
            self.handler(environ, start_response)
        except KeyError:
            pass
        
        ok_(isinstance(self.handler.request, TwodWSGIRequest))
    
    def test_actual_reason_phrase(self):
        """It must use the status phrase set by the Django response, if any."""
        environ = complete_environ(PATH_INFO="/app1/wsgi-view/")
        start_response = MockStartResponse()
        
        self.handler(environ, start_response)
        
        eq_(start_response.status, "206 One step at a time")
        
        eq_(len(start_response.response_headers), 3)
        eq_(start_response.response_headers[0][0], "Vary")
        eq_(start_response.response_headers[1][0], "X-SALUTATION")
        eq_(start_response.response_headers[2][0], "Content-Type")
    
    def test_no_actual_reason_phrase(self):
        """It must not replace the status reason if a custom one was not set."""
        environ = complete_environ(PATH_INFO="/app1/wsgi-view-ok/")
        start_response = MockStartResponse()
        
        self.handler(environ, start_response)
        
        eq_(start_response.status, "200 OK")
        
        eq_(len(start_response.response_headers), 3)
        eq_(start_response.response_headers[0][0], "Vary")
        eq_(start_response.response_headers[1][0], "X-SALUTATION")
        eq_(start_response.response_headers[2][0], "Content-Type")


#{ Tests for internal stuff


class TestStartResponse(object):
    """Tests for :class:`_StartResponseWrapper`."""
    
    def setup(self):
        self.original_sr = MockStartResponse()
        self.sr_wrapper = _StartResponseWrapper(self.original_sr)
    
    def test_no_actual_phrase(self):
        """Nothing should be changed if there's no actual status reason."""
        status = "200 Sweet"
        response_headers = [
            ("X-Foo", "Whatever"),
            ("X-Bar", "Somehow"),
            ]
        self.sr_wrapper(status, response_headers)
        ok_(self.original_sr.called)
        eq_(self.original_sr.status, status)
        eq_(len(self.original_sr.response_headers), 2)
        eq_(self.original_sr.response_headers, response_headers)
        eq_(self.original_sr.exc_info, None)
    
    def test_with_actual_phrase(self):
        """The status reason must be replaced if it's set in the headers."""
        actual_status = "200 Cool"
        response_headers = [
            ("X-Foo", "Whatever"),
            ("X-Actual-Status-Reason", actual_status),
            ]
        self.sr_wrapper("200 Sweet", response_headers)
        ok_(self.original_sr.called)
        eq_(self.original_sr.status, actual_status)
        eq_(len(self.original_sr.response_headers), 1)
        eq_(self.original_sr.response_headers, [("X-Foo", "Whatever")])
        eq_(self.original_sr.exc_info, None)


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
