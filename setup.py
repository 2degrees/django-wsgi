# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010, 2degrees Limited <gustavonarea@2degreesnetwork.com>.
# All Rights Reserved.
#
# This file is part of twod.wsgi <https://github.com/2degrees/twod.wsgi/>,
# which is subject to the provisions of the BSD at
# <http://dev.2degreesnetwork.com/p/2degrees-license.html>. A copy of the
# license should accompany this distribution. THIS SOFTWARE IS PROVIDED "AS IS"
# AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
# INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.txt")).read()
version = open(os.path.join(here, "VERSION.txt")).readline().rstrip()

setup(name="twod.wsgi",
      version=version,
      description="Enhanced WSGI support for Django applications",
      long_description=README,
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Paste",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Security",
        ],
      keywords="django wsgi paste webob web",
      author="2degrees Limited",
      author_email="2degrees-floss@googlegroups.com",
      namespace_packages=["twod"],
      url="http://packages.python.org/twod.wsgi/",
      license="BSD (http://dev.2degreesnetwork.com/p/2degrees-license.html)",
      packages=find_packages(exclude=["tests"]),
      py_modules=["django_testing", "django_testing_recipe"],
      zip_safe=False,
      tests_require = [
        "coverage",
        ],
      install_requires=[
        "Django >= 1.1",
        "WebOb >= 0.9.7, < 1.0dev",
        "Paste >= 1.7.2, <= 1.7.5.1",
        "PasteDeploy >= 1.3.3, <= 1.5.0",
        "setuptools",
        "nose",
        ],
      extras_require = {
        'buildout': ["zc.recipe.egg >= 1.2.2"],
        },
      test_suite="nose.collector",
      entry_points = """\
        [paste.app_factory]
        main = twod.wsgi.appsetup:wsgify_django
        
        [paste.composite_factory]
        full_django = twod.wsgi.factories:make_full_django_app
        
        [nose.plugins.0.10]
        django-wsgified = django_testing:DjangoWsgifiedPlugin
        
        [zc.buildout]
        nose = django_testing_recipe:DjangoWsgifiedRecipe [buildout]
      """
      )
