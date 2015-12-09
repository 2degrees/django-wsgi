# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009-2015, 2degrees Limited.
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
Tests for the use of WSGI applications within Django.

"""
from nose.tools import eq_, ok_, assert_false, assert_raises

from django_wsgi.embedded_wsgi import call_wsgi_app, make_wsgi_view
from django_wsgi.handler import DjangoWSGIRequest
from django_wsgi.exc import ApplicationCallError

from tests import (BaseDjangoTestCase, MockApp, MockClosingApp, MockWriteApp,
                   MockGeneratorApp, complete_environ)


class TestCallWSGIApp(BaseDjangoTestCase):
    """
    Tests for call_wsgi_app()
    
    """

    def test_original_environ_not_modified(self):
        """The original environ must have not been modified."""
        original_environ = \
            complete_environ(SCRIPT_NAME="/blog", PATH_INFO="/admin/models")
        expected_environ = original_environ.copy()
        request = _make_request(**original_environ)
        # Running the app:
        app = MockApp("200 OK", [])
        call_wsgi_app(app, request, "/models")
        eq_(expected_environ.keys(), request.environ.keys())
        for variable_name, expected_variable_value in expected_environ.items():
            if variable_name == 'wsgi.input':
                actual_input = request.environ['wsgi.input']
                eq_(0, actual_input.tell())
                eq_(b"", actual_input.read())
            else:
                eq_(expected_variable_value, request.environ[variable_name])

    def test_routing_args_are_removed(self):
        """The ``wsgiorg.routing_args`` environment key must be removed."""
        environ = {
            'wsgiorg.routing_args': ((), {}),
            'PATH_INFO': "/admin/models",
            }
        environ = complete_environ(**environ)
        request = _make_request(**environ)
        # Running the app:
        app = MockApp("200 OK", [])
        call_wsgi_app(app, request, "/models")
        ok_("wsgiorg.routing_args" not in app.environ)

    def test_webob_adhoc_attrs_are_removed(self):
        """WebOb's ad-hoc attributes must be removed."""
        environ = {
            'PATH_INFO': "/admin/models",
            'wsgiorg.routing_args': ((), {}),
            'webob.adhoc_attrs': {'foo': "bar"},
            }
        environ = complete_environ(**environ)
        request = _make_request(**environ)
        # Running the app:
        app = MockApp("200 OK", [])
        call_wsgi_app(app, request, "/models")
        ok_("webob.adhoc_attrs" not in app.environ)

    def test_mount_point(self):
        environ = complete_environ(SCRIPT_NAME="/dev", PATH_INFO="/trac/wiki")
        request = _make_request(**environ)
        # Running the app:
        app = MockApp("200 OK", [])
        call_wsgi_app(app, request, "/wiki")
        eq_(app.environ['SCRIPT_NAME'], "/dev/trac")
        eq_(app.environ['PATH_INFO'], "/wiki")

    def test_incorrect_mount_point(self):
        """
        WSGI apps are not run when the path left to them is not the last
        portion of the PATH_INFO in the original request.
        
        """
        environ = complete_environ(SCRIPT_NAME="/dev",
                                   PATH_INFO="/trac/wiki")
        request = _make_request(**environ)
        path_info = "/trac"
        # Running the app:
        app = MockApp("200 OK", [])
        assert_raises(ApplicationCallError, call_wsgi_app, app, request,
                      path_info)

    def test_headers_are_copied_over(self):
        environ = complete_environ(SCRIPT_NAME="/dev", PATH_INFO="/trac/wiki")
        request = _make_request(**environ)
        headers = [
            ("X-Foo", "bar"),
            ("Content-Type", "text/plain"),
            ]
        # The same headers, but set in the format used by HttpResponse
        expected_headers = {
            'x-foo': ("X-Foo", "bar"),
            'content-type': ("Content-Type", "text/plain"),
            }
        # Running the app:
        app = MockApp("200 OK", headers)
        django_response = call_wsgi_app(app, request, "/wiki")
        eq_(expected_headers, django_response._headers)

    def test_authenticated_user(self):
        environ = complete_environ(SCRIPT_NAME="/dev", PATH_INFO="/trac/wiki")
        request = _make_request(authenticated=True, **environ)
        # Running the app:
        app = MockApp("200 OK", [])
        call_wsgi_app(app, request, "/wiki")
        eq_("foobar", app.environ['REMOTE_USER'])

    def test_cookies_sent(self):
        environ = complete_environ(SCRIPT_NAME="/dev", PATH_INFO="/trac/wiki")
        request = _make_request(**environ)
        headers = [
            ("Set-Cookie", "arg1=val1"),
            ("Set-Cookie",
                "arg2=val2; expires=Fri,%2031-Dec-2010%2023:59:59%20GMT"),
            ("Set-Cookie", "arg3=val3; path=/"),
            ("Set-Cookie", "arg4=val4; path=/wiki"),
            ("Set-Cookie", "arg5=val5; domain=.example.org"),
            ("Set-Cookie", "arg6=val6; max-age=3600"),
            (
                "Set-Cookie",
                "arg7=val7; expires=Fri,%2031-Dec-2010%2023:59:59%20GMT; "
                    "max-age=3600; domain=.example.org; path=/wiki",
            ),
            # Now let's try an Unicode cookie:
            ("Set-Cookie", u"arg8=val8; max-age=3600"),
            # TODO: The "secure" cookie *attribute* is broken in SimpleCookie.
            # See: http://bugs.python.org/issue1028088
            #("Set-Cookie", "arg9=val9; secure"),
            ]
        expected_cookies = {
            'arg1': {'value': "val1"},
            'arg2': {
                'value': "val2",
                'expires': "Fri,%2031-Dec-2010%2023:59:59%20GMT",
            },
            'arg3': {'value': "val3", 'path': "/"},
            'arg4': {'value': "val4", 'path': "/wiki"},
            'arg5': {'value': "val5", 'domain': ".example.org"},
            'arg6': {'value': "val6", 'max-age': 3600},
            'arg7': {
                'value': "val7",
                'expires': "Fri,%2031-Dec-2010%2023:59:59%20GMT",
                'path': "/wiki",
                'domain': ".example.org",
                'max-age': 3600,
                },
            'arg8': {'value': "val8", 'max-age': 3600},
            # Why the next item as disabled? Check the `headers` variable above
            #'arg9': {'value': "val9", 'secure': True},
            }
        # Running the app:
        app = MockApp("200 OK", headers)
        django_response = call_wsgi_app(app, request, "/wiki")
        # Checking the cookies:
        eq_(len(expected_cookies), len(django_response.cookies))
        # Finally, let's check each cookie:
        for (cookie_set_name, cookie_set) in django_response.cookies.items():
            expected_cookie = expected_cookies[cookie_set_name]
            expected_cookie_value = expected_cookie.pop("value")
            eq_(expected_cookie_value, cookie_set.value,
                             'Cookie "%s" has a wrong value ("%s")' %
                             (cookie_set_name, cookie_set.value))
            for (attr_key, attr_val) in expected_cookie.items():
                eq_(
                    cookie_set[attr_key],
                    attr_val,
                     'Attribute "%s" in cookie %r is wrong (%r)' %
                         (attr_key, cookie_set_name, cookie_set[attr_key]),
                )

    def test_string_as_response(self):
        app = MockApp("200 It is OK", [("X-HEADER", "Foo")])
        # Running a request:
        environ = complete_environ(SCRIPT_NAME="/dev", PATH_INFO="/blog/posts")
        request = _make_request(**environ)
        django_response = call_wsgi_app(app, request, "/posts")

        http_response_content = b"body"
        eq_(http_response_content, _resolve_response_body(django_response))

    def test_iterable_as_response(self):
        app = MockGeneratorApp("200 It is OK", [("X-HEADER", "Foo")])
        # Running a request:
        environ = complete_environ(SCRIPT_NAME="/dev", PATH_INFO="/blog/posts")
        request = _make_request(**environ)
        django_response = call_wsgi_app(app, request, "/posts")

        http_response_content = b"body as iterable"
        eq_(http_response_content, _resolve_response_body(django_response))

    def test_write_response(self):
        app = MockWriteApp("200 It is OK", [("X-HEADER", "Foo")])
        # Running a request:
        environ = complete_environ(SCRIPT_NAME="/dev", PATH_INFO="/blog/posts")
        request = _make_request(**environ)
        django_response = call_wsgi_app(app, request, "/posts")

        http_response_content = b"body as iterable"
        eq_(http_response_content, _resolve_response_body(django_response))

    def test_closure_response(self):
        """The .close() method in the response (if any) must be kept."""
        app = MockClosingApp("200 It is OK", [])
        # Running a request:
        environ = complete_environ(SCRIPT_NAME="/dev", PATH_INFO="/blog/posts")
        request = _make_request(**environ)
        django_response = call_wsgi_app(app, request, "/posts")
        # Checking the .close() call:
        assert_false(app.app_iter.closed)
        django_response.close()
        ok_(app.app_iter.closed)


class TestWSGIView(BaseDjangoTestCase):
    """
    Tests for make_wsgi_view().
    
    """

    def test_right_path(self):
        """
        The WSGI application view must work when called with the right path.
        
        """
        # Loading a WSGI-powered Django view:
        headers = [("X-SALUTATION", "Hey")]
        app = MockApp("206 One step at a time", headers)
        django_view = make_wsgi_view(app)
        # Running a request:
        environ = complete_environ(SCRIPT_NAME="/dev",
                                   PATH_INFO="/app1/wsgi-view/foo/bar")
        request = _make_request(**environ)
        # Checking the response:
        django_response = django_view(request, "/foo/bar")
        eq_(django_response.status_code, 206)
        eq_(("X-SALUTATION", "Hey"), django_response._headers['x-salutation'])
        eq_(app.environ['PATH_INFO'], "/foo/bar")
        eq_(app.environ['SCRIPT_NAME'], "/dev/app1/wsgi-view")

    def test_not_final_path(self):
        """
        The path to be consumed by the WSGI app must be the end of the original
        PATH_INFO.
        
        """
        # Loading a WSGI-powered Django view:
        headers = [("X-SALUTATION", "Hey")]
        app = MockApp("206 One step at a time", headers)
        django_view = make_wsgi_view(app)
        # Running a request:
        environ = complete_environ(SCRIPT_NAME="/dev",
                                   PATH_INFO="/app1/wsgi-view/foo/bar")
        request = _make_request(**environ)
        # Checking the response. Note "/foo" is NOT the end of PATH_INFO:
        assert_raises(ApplicationCallError, django_view, request, "/foo")


#{ Test utilities


def _make_request(authenticated=False, **environ):
    """
    Make a Django request from the items in the WSGI ``environ``.
    
    """
    class MockDjangoUser(object):
        def __init__(self, authenticated):
            self.username = "foobar"
            self.authenticated = authenticated
        def is_authenticated(self):
            return self.authenticated
    request = DjangoWSGIRequest(environ)
    request.user = MockDjangoUser(authenticated)
    return request


def _resolve_response_body(response):
    body_parts = tuple(response)
    body_text = b"".join(body_parts)
    return body_text


#}
