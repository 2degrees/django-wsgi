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
"""
Utilities to set up Django applications, both in Web and CLI environments.

"""
import os
from logging import getLogger

from paste.deploy.loadwsgi import appconfig
from paste.deploy.converters import asbool, asint, aslist

from twod.wsgi.request import TwodWSGIHandler


__all__ = ("wsgify_django", "load_django")

_LOGGER = getLogger(__name__)


def wsgify_django(global_config, **local_conf):
    """
    Load the Django application for use in a WSGI server.
    
    :raises ImportError: If the Django settings module cannot be imported.
    :raises ValueError: If ``local_conf`` contains a Django setting which is
        not supported.
    :raises ValueError: If the ``django_settings_module`` directive is not set.
    :return: The Django application as a WSGI application.
    :rtype: :class:`~twod.wsgi.request.TwodWSGIHandler`
    
    """
    _set_up_settings(local_conf)
    return TwodWSGIHandler()


def load_django(config_uri):
    """
    Load the PasteDeploy settings into the Django settings module.
    
    :raises ImportError: If the Django settings module cannot be imported.
    :raises ValueError: If ``local_conf`` contains a Django setting which is
        not supported.
    :raises ValueError: If the ``django_settings_module`` directive is not set.
    
    """
    additional_settings = appconfig(config_uri)
    _set_up_settings(additional_settings)


def _set_up_settings(additional_settings):
    """
    Add the objects in ``additional_settings`` to the
    ``django_settings_module`` module.
    
    """
    django_settings_module = additional_settings.pop("django_settings_module",
                                                     None)
    if not django_settings_module:
        raise ValueError('The "django_settings_module" directive is not set')
    
    os.environ['DJANGO_SETTINGS_MODULE'] = django_settings_module
    
    _convert_settings(additional_settings)
    
    # Attaching the variables to the settings module, at least those which had
    # not been defined.
    # We need the module name for __import__ to work properly:
    # http://stackoverflow.com/questions/211100/pythons-import-doesnt-work-as-expected
    module = django_settings_module.split(".")[-1]
    settings_module = __import__(django_settings_module, additional_settings,
                                 fromlist=[module])
    
    for (setting_name, setting_value) in additional_settings.items():
        if not hasattr(settings_module, setting_name):
            # The name is not used; let's set it:
            setattr(settings_module, setting_name, setting_value)
        elif isinstance(getattr(settings_module, setting_name), tuple):
            # The name is already used by a list; let's extended it:
            new_tuple = getattr(settings_module, setting_name) + setting_value
            setattr(settings_module, setting_name, new_tuple)
        else:
            # The name is already used and it's not a list; let's warn the user:
            _LOGGER.warn('"%s" will not be overridden in %s', setting_name,
                         django_settings_module)


#{ Type casting


# Official Django settings, excerpted from
# http://docs.djangoproject.com/en/dev/ref/settings/
_DJANGO_BOOLEANS = frozenset([
    "APPEND_SLASH",
    "DEBUG",
    "DEBUG_PROPAGATE_EXCEPTIONS",
    "EMAIL_USE_TLS",
    "FORCE_SCRIPT_NAME",
    "PREPEND_WWW",
    "SEND_BROKEN_LINK_EMAILS",
    "SESSION_EXPIRE_AT_BROWSER_CLOSE",
    "SESSION_SAVE_EVERY_REQUEST",
    "TEMPLATE_DEBUG",
    "USE_ETAGS",
    "USE_I18N",
    "USE_L10N",
    "USE_THOUSAND_SEPARATOR",
    ])

_DJANGO_INTEGERS = frozenset([
    "CACHE_MIDDLEWARE_SECONDS",
    "EMAIL_PORT",
    "FILE_UPLOAD_MAX_MEMORY_SIZE",
    "FIRST_DAY_OF_WEEK",
    "MESSAGE_LEVEL",
    "NUMBER_GROUPING",
    "SESSION_COOKIE_AGE",
    "SESSION_COOKIE_SECURE",
    "SITE_ID",
    ])

_DJANGO_TUPLES = frozenset([
    "ADMIN_FOR",
    "AUTHENTICATION_BACKENDS",
    "ALLOWED_INCLUDE_ROOTS",
    "DATABASE_ROUTERS",
    "DATE_INPUT_FORMATS",
    "DATETIME_INPUT_FORMATS",
    "DISALLOWED_USER_AGENTS",
    "FILE_UPLOAD_HANDLERS",
    "FIXTURE_DIRS",
    "IGNORABLE_404_ENDS",
    "IGNORABLE_404_STARTS",
    "INSTALLED_APPS",
    "INTERNAL_IPS",
    "LOCALE_PATHS",
    "MANAGERS",
    "MIDDLEWARE_CLASSES",
    "PROFANITIES_LIST",
    "TEMPLATE_CONTEXT_PROCESSORS",
    "TEMPLATE_DIRS",
    "TEMPLATE_LOADERS",
    "TIME_INPUT_FORMATS",
    ])

_DJANGO_NESTED_TUPLES = frozenset([
    "ADMINS",
    ])

# TODO: The following settings should be supported:
_DJANGO_UNSUPPORTED_SETTINGS = frozenset([
    "FILE_UPLOAD_PERMISSIONS",
    "LANGUAGES",
    "MESSAGE_TAGS",
    "SERIALIZATION_MODULES",
    ])


def _convert_settings(settings):
    """
    Convert ``settings`` into the right types.
    
    """
    custom_booleans = aslist(settings.get("twod.booleans", ""))
    custom_integers = aslist(settings.get("twod.integers", ""))
    custom_tuples = aslist(settings.get("twod.tuples", ""))
    custom_nested_tuples = aslist(settings.get("twod.nested_tuples", ""))
    
    booleans = _DJANGO_BOOLEANS | frozenset(custom_booleans)
    integers = _DJANGO_INTEGERS | frozenset(custom_integers)
    tuples = _DJANGO_TUPLES | frozenset(custom_tuples)
    nested_tuples = _DJANGO_NESTED_TUPLES | frozenset(custom_nested_tuples)
    
    for (setting_name, setting_value) in settings.items():
        if setting_name in booleans:
            settings[setting_name] = asbool(setting_value)
        elif setting_name in integers:
            settings[setting_name] = asint(setting_value)
        elif setting_name in tuples:
            settings[setting_name] = tuple(aslist(setting_value))
        elif setting_name in nested_tuples:
            nested_tuple = tuple(
                tuple((val.strip()) for val in tuple_.strip().split(";") if val)
                for tuple_ in setting_value.splitlines()
                )
            settings[setting_name] = nested_tuple
        elif setting_name in _DJANGO_UNSUPPORTED_SETTINGS:
            raise ValueError("Setting %s is not (yet) supported; "
                             "you have to define it in your settings module." %
                             setting_name)
    
    # We should not import a module with "__file__" as a global variable:
    settings['paste_configuration_file'] = settings.pop("__file__", None)


#}
