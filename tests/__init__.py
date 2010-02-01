# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010, 2degrees Limited <gustavonarea@2degreesnetwork.com>.
# All Rights Reserved.
#
# This file is part of twod.wsgi <http://bitbucket.org/2degrees/twod.wsgi/>,
# which is subject to the provisions of the BSD at
# <http://bitbucket.org/2degrees/twod.wsgi/src/tip/LICENSE>. A copy of the
# license should accompany this distribution. THIS SOFTWARE IS PROVIDED "AS IS"
# AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
# INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Test suite for :mod:`twod.wsgi`.

"""
from StringIO import StringIO
import logging
import os

import django.conf


class BaseDjangoTestCase(object):
    """
    Base test case to set up and reset the Django settings object.
    
    """
    
    django_settings_module = "tests.fixtures.sampledjango.settings"
    
    setup_fixture = True
    
    def setup(self):
        if self.setup_fixture:
            os.environ['DJANGO_SETTINGS_MODULE'] = self.django_settings_module
        # Setting up the logging fixture:
        self.logging_handler = LoggingHandlerFixture()
        self.logs = self.logging_handler.handler.messages
    
    def teardown(self):
        self.logging_handler.undo()
        django.conf.settings = django.conf.LazySettings()
        if "DJANGO_SETTINGS_MODULE" in os.environ:
            del os.environ['DJANGO_SETTINGS_MODULE']


class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected log entries."""
    
    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())
    
    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }


class LoggingHandlerFixture(object):
    """Manager of the :class:`MockLoggingHandler`s."""
    
    def __init__(self):
        self.logger = logging.getLogger("twod.wsgi")
        self.handler = MockLoggingHandler()
        self.logger.addHandler(self.handler)
    
    def undo(self):
        self.logger.removeHandler(self.handler)


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
        write( "body")
        write(" as")
        write(" iterable")
        return []


class MockClosingApp(MockApp):
    """Mock WSGI app whose response contains a close() method."""
    
    def __init__(self, *args, **kwargs):
        super(MockClosingApp, self).__init__(*args, **kwargs)
        self.app_iter = ClosingAppIter()
    
    def __call__(self, environ, start_response):
        body = super(MockClosingApp, self).__call__(environ,start_response)
        self.app_iter.extend(body)
        return self.app_iter


class ClosingAppIter(list):
    """Mock response iterable with a close() method."""
    
    def __init__(self, *args, **kwargs):
        super(ClosingAppIter, self).__init__(*args, **kwargs)
        self.closed = False
    
    def close(self):
        self.closed = True


class MockStartResponse(object):
    """Mock start_response() callable which keeps the arguments it receives."""
    
    def __init__(self):
        self.status = None
        self.response_headers = None
        self.exc_info = None
        self.called = False
    
    def __call__(self, status, response_headers, exc_info=None):
        self.status = status
        self.response_headers = response_headers
        self.exc_info = exc_info
        self.called = True


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
