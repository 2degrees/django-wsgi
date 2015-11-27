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
Exceptions raised by :mod:`django_wsgi.`

"""

__all__ = ("DjangoWSGIException", "ApplicationCallError")


class DjangoWSGIException(Exception):
    """Base class for exceptions raised by :mod:`django_wsgi`."""
    pass


class ApplicationCallError(DjangoWSGIException):
    """
    Exception raised when an embedded WSGI application was not called properly.
    
    """
    pass
