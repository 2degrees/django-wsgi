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
Tests for the WSGI request handler.

"""
from nose.tools import eq_, ok_, assert_is_instance
from six import BytesIO
from six.moves.urllib.parse import urlencode
from webob import Request

from tests import BaseDjangoTestCase, complete_environ
from twod.wsgi.handler import DjangoApplication, TwodWSGIRequest


class TestRequest(BaseDjangoTestCase):

    @staticmethod
    def test_webob_request():
        """The WebOb request is available as a public attribute."""
        environ = complete_environ()
        twod_request = TwodWSGIRequest(environ)

        ok_(hasattr(twod_request, 'webob'))
        assert_is_instance(twod_request.webob, Request)
        eq_(twod_request.environ, twod_request.webob.environ)

    @staticmethod
    def test_request_body_read_by_django_first():
        """WebOb is able to read the request after Django."""
        twod_request = _make_stub_post_request()

        eq_(2, len(twod_request.POST))
        eq_(twod_request.POST, twod_request.webob.POST)

    @staticmethod
    def test_request_body_read_by_webob_first():
        """Django is able to read the request after WebOb."""
        twod_request = _make_stub_post_request()

        eq_(2, len(twod_request.webob.POST))
        eq_(twod_request.webob.POST, twod_request.POST)

    @staticmethod
    def test_unseekable_body_read_by_django():
        twod_request = _make_stub_post_request(_UnseekableFile)

        eq_(2, len(twod_request.POST))

    @staticmethod
    def test_unseekable_body_read_by_webob():
        twod_request = _make_stub_post_request(_UnseekableFile)

        eq_(2, len(twod_request.webob.POST))


def _make_stub_post_request(wsgi_input_class=BytesIO):
    input_ = urlencode({'foo': "bar", 'bar': "foo"}).encode()
    input_length = str(len(input_))
    environ = {
        'REQUEST_METHOD': "POST",
        'CONTENT_TYPE': "application/x-www-form-urlencoded",
        'CONTENT_LENGTH': input_length,
        'wsgi.input': wsgi_input_class(input_),
        }
    environ = complete_environ(**environ)
    twod_request = TwodWSGIRequest(environ)
    return twod_request


class TestWSGIHandler(BaseDjangoTestCase):
    """Tests for :class:`DjangoApplication`."""

    def setup(self):
        super(TestWSGIHandler, self).setup()
        self.handler = _TelltaleHandler()

    def test_right_request_class(self):
        """The WSGI handler must use Twod's request class."""
        environ = complete_environ(REQUEST_METHOD="GET", PATH_INFO="/")

        def start_response(status, response_headers): pass

        self.handler(environ, start_response)

        ok_(isinstance(self.handler.request, TwodWSGIRequest))


class _UnseekableFile(object):

    def __init__(self, text):
        super(_UnseekableFile, self).__init__()
        self._text = BytesIO(text)

    def read(self, *args, **kwargs):
        return self._text.read(*args, **kwargs)


class _TelltaleHandler(DjangoApplication):
    """
    Mock WSGI handler based on Twod's, which is going to be called once and it's
    going to store the request object it got.
    
    """

    def get_response(self, request):
        self.request = request
        return super(_TelltaleHandler, self).get_response(request)
