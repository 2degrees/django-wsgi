# -*- coding: utf-8 -*-
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
Tests for the WSGI request handler.

"""
from nose.tools import eq_, ok_, assert_is_instance
from six import BytesIO
from six.moves.urllib.parse import urlencode
from webob import Request

from tests import BaseDjangoTestCase, complete_environ
from django_wsgi.handler import APPLICATION
from django_wsgi.handler import DjangoApplication
from django_wsgi.handler import DjangoWSGIRequest


class TestRequest(BaseDjangoTestCase):

    @staticmethod
    def test_webob_request():
        """The WebOb request is available as a public attribute."""
        environ = complete_environ()
        request = DjangoWSGIRequest(environ)

        ok_(hasattr(request, 'webob'))
        assert_is_instance(request.webob, Request)
        eq_(request.environ, request.webob.environ)

    @staticmethod
    def test_request_body_read_by_django_first():
        """WebOb is able to read the request after Django."""
        request = _make_stub_post_request()

        eq_(2, len(request.POST))
        eq_(request.POST, request.webob.POST)

    @staticmethod
    def test_request_body_read_by_webob_first():
        """Django is able to read the request after WebOb."""
        request = _make_stub_post_request()

        eq_(2, len(request.webob.POST))
        eq_(request.webob.POST, request.POST)

    @staticmethod
    def test_unseekable_body_read_by_django():
        request = _make_stub_post_request(_UnseekableFile)
        eq_(2, len(request.POST))

    @staticmethod
    def test_unseekable_body_read_by_webob():
        request = _make_stub_post_request(_UnseekableFile)

        eq_(2, len(request.webob.POST))


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
    request = DjangoWSGIRequest(environ)
    return request


class TestWSGIHandler(BaseDjangoTestCase):
    """Tests for :class:`DjangoApplication`."""

    def setup(self):
        super(TestWSGIHandler, self).setup()
        self.handler = _TelltaleHandler()

    def test_right_request_class(self):
        """The WSGI handler must use the custom request class."""
        environ = complete_environ(REQUEST_METHOD="GET", PATH_INFO="/")

        def start_response(status, response_headers):
            pass

        self.handler(environ, start_response)

        ok_(isinstance(self.handler.request, DjangoWSGIRequest))


def test_handler_instance():
    assert_is_instance(APPLICATION, DjangoApplication)


class _UnseekableFile(object):

    def __init__(self, text):
        super(_UnseekableFile, self).__init__()
        self._text = BytesIO(text)

    def read(self, *args, **kwargs):
        return self._text.read(*args, **kwargs)


class _TelltaleHandler(DjangoApplication):

    def get_response(self, request):
        self.request = request
        return super(_TelltaleHandler, self).get_response(request)
