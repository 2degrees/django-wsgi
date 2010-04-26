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
WSGI and Django middleware.

"""

__all__ = ("RoutingArgsMiddleware", )


class RoutingArgsMiddleware(object):
    """
    Django middleware which implements the `wsgiorg.routing_args standard
    <http://wsgi.org/wsgi/Specifications/routing_args>`_.
    
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        request.environ['wsgiorg.routing_args'] = (view_args, view_kwargs.copy())

