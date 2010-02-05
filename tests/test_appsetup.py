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
Test the set up of the Django applications as WSGI applications.

"""
import os

from nose.tools import eq_, ok_, assert_false, assert_raises
from django.core.handlers.wsgi import WSGIHandler

from twod.wsgi.appsetup import (wsgify_django, load_django, _segregate_options,
    _set_up_settings, _convert_options, _DJANGO_BOOLEANS, _DJANGO_INTEGERS,
    _DJANGO_NESTED_TUPLES, _DJANGO_TUPLES, _DJANGO_UNSUPPORTED_SETTINGS)

from tests import BaseDjangoTestCase

_HERE = os.path.dirname(__file__)
_FIXTURES = os.path.join(_HERE, "fixtures", "sampledjango")


class TestDjangoWsgifytor(BaseDjangoTestCase):
    """Tests for :func:`wsgify_django`."""
    
    setup_fixture = False
    
    def test_it(self):
        global_conf = {
            'debug': "no",
            'django_settings_module': "tests.fixtures.sampledjango.settings",
            }
        app = wsgify_django(
            global_conf,
            FOO=10,
            debug="yes",
            )
        
        ok_(isinstance(app, WSGIHandler))
        from django.conf import settings
        assert_false(settings.DEBUG)
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
            "tests.fixtures.sampledjango.settings2")


class TestSettingUpSettings(BaseDjangoTestCase):
    """Tests for the internal :func:`_set_up_settings`."""
    
    setup_fixture = False
    
    def test_no_initial_settings(self):
        """
        Additional settings must be added even if there's no initial settings.
        
        """
        global_conf = {
            'debug': "yes",
            'django_settings_module': "tests.fixtures.empty_module",
            }
        local_conf = {
            'setting1': object(),
            'setting2': object(),
            }
        _set_up_settings(global_conf, local_conf)
        from tests.fixtures import empty_module
        
        eq_(os.environ['DJANGO_SETTINGS_MODULE'], "tests.fixtures.empty_module")
        ok_(hasattr(empty_module, "setting1"))
        ok_(hasattr(empty_module, "setting2"))
        eq_(empty_module.setting1, local_conf['setting1'])
        eq_(empty_module.setting2, local_conf['setting2'])
    
    def test_no_additional_settings(self):
        """
        The settings module must be left as is if there are no additional
        settings.
        
        """
        global_conf = {
            'debug': "yes",
            'django_settings_module': "tests.fixtures.empty_module2",
            }
        _set_up_settings(global_conf, {})
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
        global_conf = {
            'debug': "yes",
            'django_settings_module': "tests.fixtures.one_member_module",
            }
        local_conf = {
            'MEMBER': "FOO",
            }
        _set_up_settings(global_conf, local_conf)
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
        global_conf = {
            'debug': "yes",
            'django_settings_module': "tests.fixtures.list_module",
            }
        local_conf = {
            'DA_LIST': (8, 9),
            }
        _set_up_settings(global_conf, local_conf)
        from tests.fixtures import list_module
        
        eq_(os.environ['DJANGO_SETTINGS_MODULE'], "tests.fixtures.list_module")
        eq_(list_module.DA_LIST, (1, 2, 3, 8, 9))
    
    def test_non_django_settings_module(self):
        """
        ValueError must be raised if django_settings_module is not set.
        
        """
        global_conf = {
            'debug': "yes",
            }
        assert_raises(ValueError, _set_up_settings, global_conf, {})
    
    def test_DEBUG_in_python_configuration(self):
        """DEBUG must not be set in the Django settings module."""
        global_conf = {
            'django_settings_module':
                "tests.fixtures.sampledjango.debug_settings",
            }
        assert_raises(ValueError, _set_up_settings, global_conf, {})
    
    def test_non_existing_module(self):
        """
        ImportError must be propagated if the settings module doesn't exist.
        
        """
        global_conf = {
            'debug': "yes",
            'django_settings_module': "non_existing_module",
            }
        assert_raises(ImportError, _set_up_settings, global_conf, {})


class TestSettingsConvertion(object):
    """Unit tests for :func:`_convert_options`."""
    
    def test_official_booleans(self):
        """Django's boolean settings must be converted."""
        # We must exclude "DEBUG" because it's not supposed to be set in the
        # initial settings:
        booleans = _DJANGO_BOOLEANS - frozenset(["DEBUG"])
        
        for setting_name in booleans:
            global_conf = {'debug': "yes"}
            local_conf = {setting_name: "True"}
            settings = _convert_options(global_conf, local_conf)
            
            eq_(settings[setting_name],
                True,
                "%s must be a boolean, but it is %r" % (setting_name,
                                                        settings[setting_name]),
                )
    
    def test_custom_boolean(self):
        """Custom booleans should be converted."""
        global_conf = {
            'debug': "yes",
            'twod.booleans': ("mybool", ),
            }
        local_conf = {'mybool': "no"}
        settings = _convert_options(global_conf, local_conf)
        
        eq_(settings['mybool'], False)
        # "twod.booleans" should have not been added:
        assert_false("twod.booleans" in settings)
    
    def test_official_integers(self):
        """Django's integer settings must be converted."""
        for setting_name in _DJANGO_INTEGERS:
            global_conf = {'debug': "yes"}
            local_conf = {setting_name: 2}
            settings = _convert_options(global_conf, local_conf)
            
            eq_(settings[setting_name],
                2,
                "%s must be a integer, but it is %r" % (setting_name,
                                                        settings[setting_name]),
                )
    
    def test_custom_integer(self):
        """Custom integers should be converted."""
        global_conf = {
            'debug': "yes",
            'twod.integers': ("myint", ),
            }
        local_conf = {'myint': "3"}
        settings = _convert_options(global_conf, local_conf)
        
        eq_(settings['myint'], 3)
        # "twod.integers" should have not been added:
        assert_false("twod.integers" in settings)
    
    def test_official_tuples(self):
        """Django's tuple settings must be converted."""
        items = ("foo", "bar", "baz")
        for setting_name in _DJANGO_TUPLES:
            global_conf = {'debug': "yes"}
            local_conf = {setting_name: "\n    ".join(items)}
            settings = _convert_options(global_conf, local_conf)
            
            eq_(settings[setting_name], items,
                "%s must be a tuple, but it is %r" % (setting_name,
                                                      settings[setting_name]),
                )
    
    def test_custom_tuple(self):
        """Custom tuples should be converted."""
        items = ("foo", "bar", "baz")
        global_conf = {
            'debug': "yes",
            'twod.tuples': ("mytuple", ),
            }
        local_conf = {'mytuple': "\n    ".join(items)}
        settings = _convert_options(global_conf, local_conf)
        
        eq_(settings['mytuple'], items)
        # "twod.tuples" should have not been added:
        assert_false("twod.tuples" in settings)
    
    def test_official_nested_tuples(self):
        """Django's nested tuple settings must be converted."""
        items = ("foo;the bar;  baz", "bar ;foo", "baz")
        nested_items = (("foo", "the bar", "baz"), ("bar", "foo"), ("baz",))
        
        for setting_name in _DJANGO_NESTED_TUPLES:
            global_conf = {'debug': "yes"}
            local_conf = {setting_name: "\n    ".join(items)}
            settings = _convert_options(global_conf, local_conf)
            
            eq_(settings[setting_name], nested_items)
    
    def test_custom_nested_tuple(self):
        """Custom nested tuples should be converted."""
        items = ("foo;the bar;  baz", "bar ;foo", "baz")
        nested_items = (("foo", "the bar", "baz"), ("bar", "foo"), ("baz",))
        global_conf = {
            'debug': "yes",
            'twod.nested_tuples': ("my_nested_tuple", ),
            }
        local_conf = {'my_nested_tuple': "\n    ".join(items)}
        
        settings = _convert_options(global_conf, local_conf)
        
        eq_(settings['my_nested_tuple'], nested_items)
        # "twod.nested_tuples" should have not been added:
        assert_false("twod.nested_tuples" in settings)
    
    def test_strings(self):
        """
        Values whose values are not requested to be converted should be kept as
        is.
        
        """
        global_conf = {'debug': "yes"}
        local_conf = {'parameter': "value"}
        settings = _convert_options(global_conf, local_conf)
        
        ok_("parameter" in settings)
        eq_(settings['parameter'], "value")
    
    def test_unsupported_settings(self):
        """Unsupported settings are definitely not supported."""
        for setting_name in _DJANGO_UNSUPPORTED_SETTINGS:
            global_conf = {'debug': "yes"}
            local_conf = {setting_name: "foo"}
            
            assert_raises(ValueError, _convert_options, global_conf,
                          local_conf)
    
    def test__file__is_ignored(self):
        """The __file__ argument must be renamed to paste_configuration_file."""
        global_conf = {'debug': "yes", '__file__': "somewhere"}
        local_conf = {}
        
        settings = _convert_options(global_conf, local_conf)
        
        ok_("__file__" not in settings)
        ok_("paste_configuration_file" in settings)
        eq_(settings['paste_configuration_file'], "somewhere")
    
    def test_DEBUG_in_ini_config(self):
        """Django's DEBUG must not be set in the .ini configuration file."""
        bad_conf = {'DEBUG': "True"}
        # Neither in DEFAULTS:
        assert_raises(ValueError, _convert_options, bad_conf, {})
        # Nor on the application definition:
        assert_raises(ValueError, _convert_options, {}, bad_conf)
        
    
    def test_pastes_debug(self):
        """Django's "DEBUG" must be set to Paster's "debug"."""
        global_conf = {'debug': "true"}
        local_conf = {}
        settings = _convert_options(global_conf, local_conf)
        ok_("DEBUG" in settings)
        eq_(settings['DEBUG'], True)
    
    def test_no_paste_debug(self):
        """Ensure the "debug" directive for Paste is set."""
        assert_raises(ValueError, _convert_options, {}, {})


class TestOptionsSegregation(object):
    """Tests for :func:`_segregate_options`."""
    
    def test_no_reserved_option(self):
        """No reserved options will be extracted if there are none of them."""
        options = {'foo': "bar"}
        (reserved_options, free_options) = _segregate_options(options)
        
        eq_(len(reserved_options), 0)
        eq_(len(free_options), 1)
        eq_(free_options, options)
    
    def test_debug(self):
        """'debug' is a reserved option and thus should be segregated."""
        options = {'debug': "yes", 'foo': "bar"}
        (reserved_options, free_options) = _segregate_options(options)
        
        eq_(len(reserved_options), 1)
        eq_(reserved_options, {'debug': "yes"})
        eq_(len(free_options), 1)
        eq_(free_options, {'foo': "bar"})
    
    def test_django_settings(self):
        """'django_settings_module' should be segregated."""
        options = {'django_settings_module': "somewhere", 'foo': "bar"}
        (reserved_options, free_options) = _segregate_options(options)
        
        eq_(len(reserved_options), 1)
        eq_(reserved_options, {'django_settings_module': "somewhere"})
        eq_(len(free_options), 1)
        eq_(free_options, {'foo': "bar"})
    
    def test_twod_option_types(self):
        """twod.* type casting options should be segregated."""
        twod_options = {
            'twod.booleans': ("mybool",),
            'twod.integers': ("myint",),
            'twod.lists': ("mylist",),
            'twod.nested_lists': ("mynestlist",),
            }
        options = twod_options.copy()
        options['foo'] = "bar"
        
        (reserved_options, free_options) = _segregate_options(options)
        
        eq_(len(reserved_options), 4)
        eq_(reserved_options, twod_options)
        eq_(len(free_options), 1)
        eq_(free_options, {'foo': "bar"})
    
    def test_original_original_options(self):
        """The original options dictionary must not be changed."""
        options = {'django_settings_module': "somewhere", 'foo': "bar"}
        _segregate_options(options)
        
        eq_(len(options), 2)
        eq_(options['django_settings_module'], "somewhere")
        eq_(options['foo'], "bar")

