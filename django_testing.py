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
Nose plugin to run Django applications in a WSGI environment.

This module has no automated tests on purpose. Functional tests would be very
useful.

"""
from nose.plugins import Plugin
from paste.deploy import loadapp


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
        
        parser.add_option(
            "--no-db",
            action="store_true",
            default=False,
            dest="no_db",
            # We must mention "Django" so people know where the option comes
            # from:
            help="Do not set up a Django test database",
            )
    
    def configure(self, options, conf):
        """Store the URI to the PasteDeploy configuration."""
        super(DjangoWsgifiedPlugin, self).configure(options, conf)
        
        self.paste_config_uri = getattr(options, self.enableOpt)
        self.enabled = bool(self.paste_config_uri)
        self.verbosity = options.verbosity
        self.create_db = not options.no_db
    
    def begin(self):
        loadapp(self.paste_config_uri)
        # It's safe to import from Django at this point. The infamous
        # DJANGO_SETTINGS_MODULE is now set.
        
        # Setting up Django:
        from django.test.utils import setup_test_environment
        setup_test_environment()
        
        # Setting up the database:
        if self.create_db:
            from django.conf import settings
            from django.db import connection
            
            self.db_name = settings.DATABASE_NAME
            connection.creation.create_test_db(self.verbosity, autoclobber=True)
    
    def finalize(self, result=None):
        from django.test.utils import teardown_test_environment
        teardown_test_environment()
        # Tearing down the database:
        if self.create_db:
            from django.db import connection
            connection.creation.destroy_test_db(self.db_name, self.verbosity)
