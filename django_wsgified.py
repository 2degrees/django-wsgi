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
Nose plugin to run Django applications in a WSGI environment.

This module has no automated tests on purpose, because it's very complex to
test and we don't have enough time to implement them.

"""
from nose.plugins import Plugin

__all__ = ("DjangoWsgifiedPlugin",)


class DjangoWsgifiedPlugin(Plugin):
    """
    Loads the Django application described by the PasteDeploy configuration URL
    in a WSGI environment suitable for testing.
    
    """
    enabled = False
    
    name = "django-wsgified"
    
    enableOpt = "paste_config_uri"
    
    def options(self, parser, env):
        help = (
            "Load the Django application described by the PasteDeploy "
            "configuration URI in a WSGI environment suitable for testing."
        )
        
        parser.add_option(
            "--with-%s" % self.name,
            type="string",
            default="",
            dest=self.enableOpt,
            help=help,
            )
    
    def configure(self, options, conf):
        """Store the URI to the PasteDeploy configuration."""
        super(DjangoWsgifiedPlugin, self).configure(options, conf)
        
        self.paste_config_uri = getattr(options, self.enableOpt)
        self.enabled = bool(self.paste_config_uri)
    
    def begin(self):
        # We have to import here to avoid corrupting the coverage report for
        # twod.wsgi itself:
        from twod.wsgi.appsetup import load_django
        
        load_django(self.paste_config_uri)
