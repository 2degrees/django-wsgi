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

from twod.wsgi import TwodResponse
from twod.wsgi.exc import ApplicationCallError


__all__ = ("call_wsgi_app", "make_wsgi_view")


def call_wsgi_app(wsgi_app, request, path_info):
    """
    Call the ``wsgi_app`` with ``request`` and return its response.
    
    :param wsgi_app: The WSGI application to be run.
    :type wsgi_app: callable
    :param request: The Django request.
    :type request: :class:`twod.wsgi.handler.TwodWSGIRequest`
    :param path_info: The ``PATH_INFO`` to be used by the WSGI application.
    :type path: :class:`basestring`
    :raises twod.wsgi.exc.ApplicationCallError: If ``path_info`` is not the
        last portion of the ``PATH_INFO`` in ``request``.
    :return: The response from the WSGI application, turned into a Django
        response.
    :rtype: :class:`twod.wsgi.TwodResponse`
    
    """
    new_request = request.copy()
    
    # Moving the portion of the path consumed by the current view, from the
    # PATH_INTO to the SCRIPT_NAME:
    if not request.path_info.endswith(path_info):
        raise ApplicationCallError("Path %s is not the last portion of the "
                                   "PATH_INFO in the original request (%s)"
                                   % (path_info, request.path_info))
    consumed_path = request.path_info[:-len(path_info)]
    new_request.path_info = path_info
    new_request.script_name = request.script_name + consumed_path
    
    # If the user has been authenticated in Django, log him in the WSGI app:
    if request.user.is_authenticated():
        new_request.remote_user = request.user.username
    
    # Cleaning the routing_args, if any. The application should have its own
    # arguments, without relying on any arguments from a parent application:
    if "wsgiorg.routing_args" in request.environ:
        del new_request.environ['wsgiorg.routing_args']
    # And the same for the WebOb ad-hoc attributes:
    if "webob.adhoc_attrs" in request.environ:
        del new_request.environ['webob.adhoc_attrs']
    
    # Calling the WSGI application and getting its response:
    (status, headers, body) = new_request.call_application(wsgi_app)
    
    # Turning its response into a Django response:
    cookies = SimpleCookie()
    django_response = TwodResponse(body, status=status)
    for (header, value) in headers:
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


def make_wsgi_view(wsgi_app):
    """
    Return a callable which can be used as a Django view powered by the
    ``wsgi_app``.
    
    :param wsgi_app: The WSGI which will run the view.
    :return: The view callable.
    
    """
    
    def view(request, path_info):
        return call_wsgi_app(wsgi_app, request, path_info)
    
    return view

