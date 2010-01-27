# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010, 2degrees Limited <gustavonarea@2degreesnetwork.com>.
# All Rights Reserved.
#
# This file is part of twod.wsgi <http://bitbucket.org/Gustavo/twod.wsgi/>.
#
# twod.wsgi is subject to the provisions of the MIT/X license at
# <http://www.opensource.org/licenses/mit-license.php>.  A copy of the license
# should accompany this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY
# AND ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
# INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################
from tests.fixtures.sampledjango import settings
"""
Test the set up of the Django applications as WSGI applications.

"""
import os

from nose.tools import eq_, ok_, assert_raises
from django.core.handlers.wsgi import WSGIHandler

from twod.wsgi.appsetup import (wsgify_django, load_django, _set_up_settings,
    _convert_settings, _DJANGO_BOOLEANS, _DJANGO_INTEGERS,
    _DJANGO_NESTED_TUPLES, _DJANGO_TUPLES, _DJANGO_UNSUPPORTED_SETTINGS)

from tests import BaseDjangoTestCase

_HERE = os.path.dirname(__file__)
_FIXTURES = os.path.join(_HERE, "fixtures", "sampledjango")


class TestDjangoWsgifytor(BaseDjangoTestCase):
    """Tests for :func:`wsgify_django`."""
    
    setup_fixture = False
    
    def test_it(self):
        app = wsgify_django(
            {},
            django_settings_module="tests.fixtures.sampledjango.settings",
            FOO=10,
            )
        ok_(isinstance(app, WSGIHandler))
        from django.conf import settings
        eq_(settings.FOO, 10)


class TestDjangoLoader(BaseDjangoTestCase):
    """Tests for :func:`load_django`."""
    
    setup_fixture = False
    
    def test_it(self):
        config = "config:" + os.path.join(_FIXTURES, "simplest-conf.ini")
        load_django(config)
        
        from django.conf import settings
        eq_(settings.BAR, "20")
        ok_("DJANGO_SETTINGS_MODULE" in os.environ)
        eq_(os.environ['DJANGO_SETTINGS_MODULE'],
            "tests.fixtures.sampledjango.settings")


class TestSettingUpSettings(BaseDjangoTestCase):
    """Tests for the internal :func:`_set_up_settings`."""
    
    setup_fixture = False
    
    def test_no_initial_settings(self):
        """
        Additional settings must be added even if there's no initial settings.
        
        """
        additional_settings = {
            'setting1': object(),
            'setting2': object(),
            'django_settings_module': "tests.fixtures.empty_module",
            }
        _set_up_settings(additional_settings)
        from tests.fixtures import empty_module
        
        eq_(os.environ['DJANGO_SETTINGS_MODULE'], "tests.fixtures.empty_module")
        ok_(hasattr(empty_module, "setting1"))
        ok_(hasattr(empty_module, "setting2"))
        eq_(empty_module.setting1, additional_settings['setting1'])
        eq_(empty_module.setting2, additional_settings['setting2'])
    
    def test_no_additional_settings(self):
        """
        The settings module must be left as is if there are no additional
        settings.
        
        """
        settings = {'django_settings_module': "tests.fixtures.empty_module2"}
        _set_up_settings(settings)
        from tests.fixtures import empty_module2
        
        eq_(os.environ['DJANGO_SETTINGS_MODULE'], "tests.fixtures.empty_module2")
        # Ignoring the built-in members:
        scope = [value for value in dir(empty_module2)
                 if not value.startswith("__") and value.endswith("__")]
        eq_(len(scope), 0)
    
    def test_name_clash(self):
        """
        Additional settings must not override initial values in settings.py.
        
        """
        additional_settings = {
            'MEMBER': "FOO",
            'django_settings_module': "tests.fixtures.one_member_module",
            }
        _set_up_settings(additional_settings)
        from tests.fixtures import one_member_module
        
        eq_(os.environ['DJANGO_SETTINGS_MODULE'],
            "tests.fixtures.one_member_module")
        eq_(one_member_module.MEMBER, "MEMBER")
        ok_(len(self.logs['warning']), 1)
        eq_('"MEMBER" will not be overridden in tests.fixtures.one_member_module',
            self.logs['warning'][0])
    
    def test_list(self):
        """
        Additional settings can extend lists in the original module.
        
        """
        additional_settings = {
            'DA_LIST': (8, 9),
            'django_settings_module': "tests.fixtures.list_module",
            }
        _set_up_settings(additional_settings)
        from tests.fixtures import list_module
        
        eq_(os.environ['DJANGO_SETTINGS_MODULE'], "tests.fixtures.list_module")
        eq_(list_module.DA_LIST, (1, 2, 3, 8, 9))
    
    def test_non_django_settings_module(self):
        """
        ValueError must be raised if django_settings_module is not set.
        
        """
        additional_settings = {}
        assert_raises(ValueError, _set_up_settings, additional_settings)
    
    def test_non_existing_module(self):
        """
        ImportError must be propagated if the settings module doesn't exist.
        
        """
        additional_settings = {'django_settings_module': "non_existing_module"}
        assert_raises(ImportError, _set_up_settings, additional_settings)


class TestSettingsConvertion(object):
    """Unit tests for :func:`_convert_settings`."""
    
    def test_official_booleans(self):
        """Django's boolean settings must be converted."""
        for setting_name in _DJANGO_BOOLEANS:
            settings = {setting_name: "True"}
            _convert_settings(settings)
            eq_(settings[setting_name],
                True,
                "%s must be a boolean, but it is %r" % (setting_name,
                                                        settings[setting_name]),
                )
    
    def test_custom_boolean(self):
        """Custom booleans should be converted."""
        settings = {
            'twod.booleans': ("mybool", ),
            'mybool': "no",
            }
        _convert_settings(settings)
        eq_(settings['mybool'], False)
    
    def test_official_integers(self):
        """Django's integer settings must be converted."""
        for setting_name in _DJANGO_INTEGERS:
            settings = {setting_name: 2}
            _convert_settings(settings)
            eq_(settings[setting_name],
                2,
                "%s must be a integer, but it is %r" % (setting_name,
                                                        settings[setting_name]),
                )
    
    def test_custom_integer(self):
        """Custom integers should be converted."""
        settings = {
            'twod.integers': ("myint", ),
            'myint': "3",
            }
        _convert_settings(settings)
        eq_(settings['myint'], 3)
    
    def test_official_tuples(self):
        """Django's tuple settings must be converted."""
        items = ("foo", "bar", "baz")
        for setting_name in _DJANGO_TUPLES:
            settings = {setting_name: "\n    ".join(items)}
            _convert_settings(settings)
            eq_(settings[setting_name], items,
                "%s must be a tuple, but it is %r" % (setting_name,
                                                      settings[setting_name]),
                )
    
    def test_custom_tuple(self):
        """Custom tuples should be converted."""
        items = ("foo", "bar", "baz")
        settings = {
            'twod.tuples': ("mytuple", ),
            'mytuple': "\n    ".join(items),
            }
        _convert_settings(settings)
        eq_(settings['mytuple'], items)
    
    def test_official_nested_tuples(self):
        """Django's nested tuple settings must be converted."""
        items = ("foo;the bar;  baz", "bar ;foo", "baz")
        nested_items = (("foo", "the bar", "baz"), ("bar", "foo"), ("baz",))
        for setting_name in _DJANGO_NESTED_TUPLES:
            settings = {setting_name: "\n    ".join(items)}
            _convert_settings(settings)
            eq_(settings[setting_name], nested_items)
    
    def test_custom_nested_tuple(self):
        """Custom nested tuples should be converted."""
        items = ("foo;the bar;  baz", "bar ;foo", "baz")
        nested_items = (("foo", "the bar", "baz"), ("bar", "foo"), ("baz",))
        settings = {
            'twod.nested_tuples': ("my_nested_tuple", ),
            'my_nested_tuple': "\n    ".join(items),
            }
        _convert_settings(settings)
        eq_(settings['my_nested_tuple'], nested_items)
    
    def test_strings(self):
        """
        Values whose values are not requested to be converted should be kept as
        is.
        
        """
        settings = {'parameter': "value"}
        _convert_settings(settings)
        eq_(settings['parameter'], "value")
    
    def test_unsupported_settings(self):
        """Unsupported settings are definitely not supported."""
        for setting_name in _DJANGO_UNSUPPORTED_SETTINGS:
            assert_raises(ValueError, _convert_settings, {setting_name: "foo"})
    
    def test__file__is_igored(self):
        """The __file__ argument must be renamed to paste_configuration_file."""
        settings = {'__file__': "somewhere"}
        _convert_settings(settings)
        ok_("__file__" not in settings)
        ok_("paste_configuration_file" in settings)
        eq_(settings['paste_configuration_file'], "somewhere")
