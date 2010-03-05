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
Enhanced WSGI support for Django applications.

"""

# Importing elements that should be available from this namespace:
from twod.wsgi.handler import DjangoApplication, TwodResponse
from twod.wsgi.middleware import RoutingArgsMiddleware
from twod.wsgi.embedded_wsgi import call_wsgi_app, make_wsgi_view
from twod.wsgi.appsetup import wsgify_django

__all__ = ("DjangoApplication", "TwodResponse", "RoutingArgsMiddleware",
           "call_wsgi_app", "make_wsgi_view", "wsgify_django")
