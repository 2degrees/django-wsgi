# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010, 2013, 2degrees Limited.
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
Test suite for :mod:`django_wsgi`.

"""
import os

from six import StringIO
from django import conf
from django.conf import LazySettings


_DJANGO_SETTINGS_MODULE = "tests.dummy_django_project.settings"
os.environ['DJANGO_SETTINGS_MODULE'] = _DJANGO_SETTINGS_MODULE


class BaseDjangoTestCase(object):

    def setup(self):
        self.__reset_settings()

    def teardown(self):
        self.__reset_settings()

    @staticmethod
    def __reset_settings():
        os.environ['DJANGO_SETTINGS_MODULE'] = _DJANGO_SETTINGS_MODULE
        conf.settings = LazySettings()


#{ Mock WSGI apps


class MockApp(object):
    """
    Mock WSGI application.
    
    """

    def __init__(self, status, headers):
        self.status = status
        self.headers = headers

    def __call__(self, environ, start_response):
        self.environ = environ
        start_response(self.status, self.headers)
        return ["body"]


class MockGeneratorApp(MockApp):
    """
    Mock WSGI application that returns an iterator.
    
    """

    def __call__(self, environ, start_response):
        self.environ = environ
        start_response(self.status, self.headers)
        def gen():
            yield "body"
            yield " as"
            yield " iterable"
        return gen()


class MockWriteApp(MockApp):
    """
    Mock WSGI app which uses the write() function.
    
    """

    def __call__(self, environ, start_response):
        self.environ = environ
        write = start_response(self.status, self.headers)
        write("body")
        write(" as")
        write(" iterable")
        return []


class MockClosingApp(MockApp):
    """Mock WSGI app whose response contains a close() method."""

    def __init__(self, *args, **kwargs):
        super(MockClosingApp, self).__init__(*args, **kwargs)
        self.app_iter = ClosingAppIter()

    def __call__(self, environ, start_response):
        body = super(MockClosingApp, self).__call__(environ, start_response)
        self.app_iter.extend(body)
        return self.app_iter


class ClosingAppIter(list):
    """Mock response iterable with a close() method."""

    def __init__(self, *args, **kwargs):
        super(ClosingAppIter, self).__init__(*args, **kwargs)
        self.closed = False

    def close(self):
        self.closed = True


def complete_environ(**environ):
    """
    Add the missing items in ``environ``.
    
    """
    full_environ = {
        'REQUEST_METHOD': "GET",
        'SERVER_NAME': "example.org",
        'SERVER_PORT': "80",
        'SERVER_PROTOCOL': "HTTP/1.1",
        'HOST': "example.org",
        'wsgi.input': StringIO(""),
        'wsgi.url_scheme': "http",
        }
    full_environ.update(environ)
    return full_environ

#}
