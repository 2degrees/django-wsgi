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
Utilities to set up Django applications, both in Web and CLI environments.

"""
import os
from logging import getLogger

from paste.deploy.loadwsgi import appconfig
from paste.deploy.converters import asbool, asint, aslist

from twod.wsgi.handler import DjangoApplication


__all__ = ("wsgify_django", )

_LOGGER = getLogger(__name__)


def wsgify_django(global_config, **local_conf):
    """
    Load the Django application for use in a WSGI server.
    
    :raises ImportError: If the Django settings module cannot be imported.
    :raises ValueError: If ``local_conf`` contains a Django setting which is
        not supported.
    :raises ValueError: If the ``django_settings_module`` directive is not set.
    :raises ValueError: If Django's ``DEBUG`` is set instead of Paste's
        ``debug``.
    :return: The Django application as a WSGI application.
    :rtype: :class:`~twod.wsgi.handler.DjangoApplication`
    
    """
    _set_up_settings(global_config, local_conf)
    return DjangoApplication()


def _set_up_settings(global_conf, local_conf):
    """
    Add the PasteDeploy options to the DJANGO_SETTINGS_MODULE module.
    
    """
    django_settings_module = global_conf.get("django_settings_module")
    if not django_settings_module:
        raise ValueError('The "django_settings_module" directive is not set')
    
    os.environ['DJANGO_SETTINGS_MODULE'] = django_settings_module
    
    # Attaching the variables to the settings module, at least those which had
    # not been defined.
    # We need the module name for __import__ to work properly:
    # http://stackoverflow.com/questions/211100/pythons-import-doesnt-work-as-expected
    module = django_settings_module.split(".")[-1]
    settings_module = __import__(django_settings_module, fromlist=[module])
    
    if hasattr(settings_module, "DEBUG"):
        raise ValueError('Module %s must not define "DEBUG". It must be set '
                         'in the PasteDesploy configuration file as "debug".' %
                         django_settings_module)
    
    options = _convert_options(global_conf, local_conf)
    
    for (setting_name, setting_value) in options.items():
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
    "MIDDLEWARE_CLASSES",
    "PROFANITIES_LIST",
    "TEMPLATE_CONTEXT_PROCESSORS",
    "TEMPLATE_DIRS",
    "TEMPLATE_LOADERS",
    "TIME_INPUT_FORMATS",
    ])

_DJANGO_NESTED_TUPLES = frozenset([
    "ADMINS",
    "MANAGERS",
    ])

_DJANGO_DICTIONARIES = frozenset(["DATABASE_OPTIONS"])

# TODO: The following settings should be supported:
_DJANGO_UNSUPPORTED_SETTINGS = frozenset([
    "FILE_UPLOAD_PERMISSIONS",
    "LANGUAGES",
    "MESSAGE_TAGS",
    "SERIALIZATION_MODULES",
    ])


def _convert_options(global_conf, local_conf):
    """
    Build the final options based on PasteDeploy's ``global_conf`` and
    ``local_conf``.
    
    """
    # First of all, let's make sure Django will use Paste's "debug" value:
    if "DEBUG" in global_conf or "DEBUG" in local_conf:
        raise ValueError("Do not set Django's DEBUG in the configuration file; "
                         "use Paste's 'debug' instead")
    if "debug" not in global_conf:
        raise ValueError("Paste's 'debug' option must be set in the "
                         "configuration file")
    
    local_conf['DEBUG'] = global_conf['debug']
    
    # Now it's safe to move on with the type casting:
    
    custom_booleans = aslist(global_conf.get("twod.booleans", ""))
    custom_integers = aslist(global_conf.get("twod.integers", ""))
    custom_tuples = aslist(global_conf.get("twod.tuples", ""))
    custom_nested_tuples = aslist(global_conf.get("twod.nested_tuples", ""))
    custom_dictionaries = aslist(global_conf.get("twod.dictionaries", ""))
    
    booleans = _DJANGO_BOOLEANS | frozenset(custom_booleans)
    integers = _DJANGO_INTEGERS | frozenset(custom_integers)
    tuples = _DJANGO_TUPLES | frozenset(custom_tuples)
    nested_tuples = _DJANGO_NESTED_TUPLES | frozenset(custom_nested_tuples)
    dictionaries = _DJANGO_DICTIONARIES | frozenset(custom_dictionaries)
    
    options = {}
    for (option_name, option_value) in local_conf.items():
        if option_name in booleans:
            options[option_name] = asbool(option_value)
        elif option_name in integers:
            options[option_name] = asint(option_value)
        elif option_name in tuples:
            options[option_name] = tuple(aslist(option_value))
        elif option_name in nested_tuples:
            nested_tuple = tuple(
                tuple((val.strip()) for val in tuple_.strip().split(";") if val)
                for tuple_ in option_value.strip().splitlines()
                )
            options[option_name] = nested_tuple
        elif option_name in dictionaries:
            lines = option_value.strip().splitlines()
            items = [option.strip().split("=", 1) for option in lines]
            dictionary = dict(
                (key.strip(), value.strip()) for (key, value) in items
                )
            options[option_name] = dictionary
        elif option_name in _DJANGO_UNSUPPORTED_SETTINGS:
            raise ValueError("Django setting %s is not (yet) supported; "
                             "you have to define it in your options module." %
                             option_name)
        else:
            # Store the option as an string:
            options[option_name] = option_value
    
    # We should not import a module with "__file__" as a global variable:
    options['paste_configuration_file'] = global_conf.get("__file__")
    
    return options


#}
