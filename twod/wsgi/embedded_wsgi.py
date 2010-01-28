# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009-2010, 2degrees Limited <gustavonarea@2degreesnetwork.com>.
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
Utilities to use WSGI applications within Django.

"""

from Cookie import SimpleCookie
from itertools import chain

from django.http import HttpResponse


__all__ = ("call_wsgi_app", "make_wsgi_view")


def call_wsgi_app(wsgi_app, request, mount_point=None):
    """
    Call the ``wsgi_app`` with ``request`` and return its response.
    
    :param wsgi_app: The WSGI application to be run.
    :type wsgi_app: callable
    :param request: The Django request.
    :type request: :class:`django.http.HttpRequest`
    :param mount_point: The path where the WSGI application should be mounted.
    :type mount_point: regex pattern or :class:`basestring`
    :return: The response from the WSGI application, turned into a Django
        response.
    :rtype: :class:`django.http.HttpResponse`
    
    If ``mount_point`` is not present, the URL matched for the current request
    in Django will be used -- This is the desired behavior is most situations.
    
    """
    environ = request.environ.copy()
    
    # Moving the portion of the path consumed by the current view, from the
    # PATH_INTO to the SCRIPT_NAME:
    final_mount_point = mount_point or request.matched_url_regex
    if isinstance(final_mount_point, basestring):
        # It's already an string, so we just have to make sure it's valid:
        if not environ['PATH_INFO'].startswith(final_mount_point):
            raise ValueError("Path %s has not been consumed in PATH_INFO" %
                             final_mount_point)
    else:
        # It's a regular expression:
        match = final_mount_point.search(environ['PATH_INFO'][1:])
        if not match:
            regex = final_mount_point.pattern
            raise ValueError("Path pattern %s has not been consumed in "
                             "PATH_INFO" % regex)
        final_mount_point = "/%s" % match.group()
    environ['PATH_INFO'] = environ['PATH_INFO'][len(final_mount_point):]
    environ['SCRIPT_NAME'] = environ['SCRIPT_NAME'] + final_mount_point
    
    # If the user has been authenticated in Django, log him in the WSGI app:
    if request.user.is_authenticated():
        environ['REMOTE_USER'] = request.user.username
    
    # Cleaning the routing_args, if any. The application should have its own
    # arguments, without relying on any arguments from a parent application:
    if "wsgiorg.routing_args" in environ:
        del environ['wsgiorg.routing_args']
    
    # Calling the WSGI application and getting its response:
    response_wrapper = _ResponseStarter()
    wsgi_response = wsgi_app(environ, response_wrapper)
    body = chain(response_wrapper.body, wsgi_response)
    
    # Turning its response into a Django response:
    cookies = SimpleCookie()
    django_response = HttpResponse(body, status=response_wrapper.status)
    for (header, value) in response_wrapper.response_headers:
        if header.upper() == "SET-COOKIE":
            if isinstance(value, unicode):
                # It can't be Unicode:
                value = value.encode("us-ascii")
            cookies.load(value)
        else:
            django_response[header] = value
    
    # Setting the cookies from Django:
    for (cookie_name, cookie) in cookies.items():
        cookie_attributes = {
            'key': cookie_name,
            'value': cookie.value,
            'max_age': cookie.get("max-age"),
            'expires': cookie.get("expires"),
            'path': cookie.get("path", "/"),
            'domain': cookie.get("domain"),
            }
        django_response.set_cookie(**cookie_attributes)
    return django_response


def make_wsgi_view(wsgi_app, mount_point=None):
    """
    Return a callable which can be used as a Django view powered by the
    ``wsgi_app``.
    
    :param wsgi_app: The WSGI which will run the view.
    :return: The callable.
    
    """
    def view(request):
        return call_wsgi_app(wsgi_app, request, mount_point)
    return view


#{ Internal WSGI stuff


class _ResponseStarter(object):
    """
    Callable to be used as ``start_response`` in order to extract the HTTP
    status code and headers.
    
    """
    
    def __init__(self):
        self.status = None
        self.response_headers = []
        self.exc_info = None
        self.body = []
    
    def __call__(self, status, response_headers, exc_info=None):
        self.status = int(status[:3])
        self.response_headers = response_headers
        # exc_info is not used at all. It does not seem to be possible to use
        # it in Django.
        self.exc_info = exc_info
        
        def write(data):
            self.body.append(data)
        
        return write


#}
