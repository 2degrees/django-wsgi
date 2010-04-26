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
Miscellaneous PasteDeploy Application Factories.

"""
from os import path

from paste.urlmap import URLMap
from paste.urlparser import StaticURLParser
from django import __file__ as django_init


__all__ = ("make_full_django_app", "add_media_to_app")


_DJANGO_ROOT = path.dirname(django_init)


def make_full_django_app(loader, global_conf, **local_conf):
    """
    Return a WSGI application made up of the Django application, its media and
    the Django Admin media.
    
    This is a PasteDeploy Composite Application Factory.
    
    """
    django_app = loader.get_app(local_conf['django_app'], global_conf=global_conf)
    return add_media_to_app(django_app)


def add_media_to_app(django_app):
    """
    Return a WSGI application made up of the Django application, its media and
    the Django Admin media.
    
    """
    app = URLMap()
    app['/'] = django_app
    
    # The Django App has been loaded, so it's now safe to access the settings:
    from django.conf import settings
    
    # Setting up the Admin media:
    admin_media = path.join(_DJANGO_ROOT, "contrib", "admin", "media")
    app[settings.ADMIN_MEDIA_PREFIX] = StaticURLParser(admin_media)
    
    # Setting up the media for the Django application:
    app[settings.MEDIA_URL] = StaticURLParser(settings.MEDIA_ROOT)
    
    return app
    

