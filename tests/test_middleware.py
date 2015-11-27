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
Tests for the Django middleware.

"""
import os

from nose.tools import eq_, ok_

from django_wsgi.middleware import RoutingArgsMiddleware

os.environ['DJANGO_SETTINGS_MODULE'] = "tests.fixtures.sampledjango"


class TestRoutingArgs(object):
    """Tests for the wsgiorg.routing_args middleware."""
    
    def setup(self):
        self.mw = RoutingArgsMiddleware()
        self.request = MockRequest({})
    
    def test_arguments_are_stored(self):
        """The positional and named arguments should be stored in the environ"""
        args = ("foo", "bar")
        kwargs = {'arg': "value"}
        self.mw.process_view(self.request, MOCK_VIEW, args, kwargs)
        ok_("wsgiorg.routing_args" in self.request.environ)
        eq_(len(self.request.environ['wsgiorg.routing_args']), 2)
        eq_(self.request.environ['wsgiorg.routing_args'][0], args)
        eq_(self.request.environ['wsgiorg.routing_args'][1], kwargs)
    
    def test_named_arguments_are_copied(self):
        """
        The named arguments must be copied, not passed by reference.
        
        Because Django will pass them on without inspecting the arguments for
        the view, unlike other frameworks like Pylons.
        
        """
        kwargs = {'arg': "value"}
        self.mw.process_view(self.request, MOCK_VIEW, ("foo", "bar"), kwargs)
        self.request.environ['wsgiorg.routing_args'][1]['new_arg'] = "new_value"
        # The original dictionary must have not been modified:
        eq_(len(kwargs), 1)
        ok_("arg" in kwargs)
    
    def test_no_response(self):
        """A response should never be returned."""
        args = ("foo", "bar")
        kwargs = {'arg': "value"}
        result = self.mw.process_view(self.request, MOCK_VIEW, args, kwargs)
        ok_(result is None)


#{ Mock objects


MOCK_VIEW = lambda request: "response"


class MockRequest(object):
    """
    Mock Django request class.
    
    This way we won't need to set the DJANGO_SETTINGS_MODULE.
    
    """
    
    def __init__(self, environ):
        self.environ = environ


#}
