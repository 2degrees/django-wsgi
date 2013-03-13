# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010, 2013, 2degrees Limited.
# All Rights Reserved.
#
# This file is part of twod.wsgi <https://github.com/2degrees/twod.wsgi/>,
# which is subject to the provisions of the BSD at
# <http://dev.2degreesnetwork.com/p/2degrees-license.html>. A copy of the
# license should accompany this distribution. THIS SOFTWARE IS PROVIDED "AS IS"
# AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
# INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Exceptions raised by :mod:`twod.wsgi.`

"""

__all__ = ("TwodWSGIException", "ApplicationCallError")


class TwodWSGIException(Exception):
    """Base class for exceptions raised by :mod:`twod.wsgi`."""
    pass


class ApplicationCallError(TwodWSGIException):
    """
    Exception raised when an embedded WSGI application was not called properly.
    
    """
    pass
