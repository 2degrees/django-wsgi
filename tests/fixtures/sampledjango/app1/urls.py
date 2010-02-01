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
URL definitions for the mock Django application.

"""

from django.conf.urls.defaults import patterns

from twod.wsgi import make_wsgi_view

from tests import MockApp
from tests.fixtures.sampledjango import mock_view

app = make_wsgi_view(MockApp("206 One step at a time",
                             [("X-SALUTATION", "Hey")]))

ok_app = make_wsgi_view(MockApp("200 OK", [("X-SALUTATION", "Hey")]))

urlpatterns = patterns('',
    (r'^blog', mock_view),
    (r'^admin', mock_view),
    (r'^secret', mock_view),
    (r"wsgi-view-ok(/.*)?", ok_app),
    (r"wsgi-view(/.*)?", app),
    )
