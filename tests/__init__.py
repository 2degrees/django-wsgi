# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010, 2degrees Limited <gustavonarea@2degreesnetwork.com>.
# All Rights Reserved.
#
# This file is part of twod.wsgi <http://bitbucket.org/Gustavo/twod.wsgi/>,
# which is subject to the provisions of the BSD at
# <http://bitbucket.org/Gustavo/twod.wsgi/src/tip/LICENSE>. A copy of the
# license should accompany this distribution. THIS SOFTWARE IS PROVIDED "AS IS"
# AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
# INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Test suite for :mod:`twod.wsgi`.

"""
import logging
import os

import django.conf


class BaseDjangoTestCase(object):
    """
    Base test case to set up and reset the Django settings object.
    
    """
    
    django_settings_module = "tests.fixtures.sampledjango.settings"
    
    setup_fixture = True
    
    def setup(self):
        if self.setup_fixture:
            os.environ['DJANGO_SETTINGS_MODULE'] = self.django_settings_module
        # Setting up the logging fixture:
        self.logging_handler = LoggingHandlerFixture()
        self.logs = self.logging_handler.handler.messages
    
    def teardown(self):
        self.logging_handler.undo()
        django.conf.settings = django.conf.LazySettings()
        if "DJANGO_SETTINGS_MODULE" in os.environ:
            del os.environ['DJANGO_SETTINGS_MODULE']


class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected log entries."""
    
    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())
    
    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }


class LoggingHandlerFixture(object):
    """Manager of the :class:`MockLoggingHandler`s."""
    
    def __init__(self):
        self.logger = logging.getLogger("twod.wsgi")
        self.handler = MockLoggingHandler()
        self.logger.addHandler(self.handler)
    
    def undo(self):
        self.logger.removeHandler(self.handler)
