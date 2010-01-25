# -*- coding: utf-8 -*-
"""
URL definitions for the mock Django application.

"""

from django.conf.urls.defaults import patterns

from tests.fixtures.sampledjango import mock_view

urlpatterns = patterns('',
    (r'^secret', mock_view),
    (r'^nothing', mock_view),
    )


