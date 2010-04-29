===================
About **twod.wsgi**
===================

*twod.wsgi* has only one goal, which is to bring WSGI support to Django
to the same level as in the other modern Python frameworks. We tried it to
implement these improvements at the core of Django, but unfortunately `that
is not going to happen
<http://groups.google.com/group/django-developers/browse_thread/thread/08c7ffeee7b9343c>`_
for the time being.

If we succeed and make Django developers realise how critical interoperability
with and reusability of **existing 3rd party software** are, we may see these
improvements in Django 1.3. And you can do your bit by `supporting twod.wsgi`_.

This is another project brought to you by `2degrees Limited
<http://dev.2degreesnetwork.com>`_.


Getting help
============

Keep in mind that **twod.wsgi is a thin integration layer**, so if you have
questions about the 3rd party software mentioned in the :doc:`manual
<manual/index>`, it's best to use the support channels for that particular
project.

For questions about WebOb, WebTest, PasteDeploy, PasteScript and Paste itself,
use the `paste-users mailing list <http://groups.google.com/group/paste-users>`_.
Nose has its `nose-users mailing list
<http://groups.google.com/group/nose-users>`_ and the preferred support channel
for Buildout is `Python's Distutils-SIG
<http://mail.python.org/mailman/listinfo/distutils-sig>`_. `Python's Web-SIG
<http://mail.python.org/mailman/listinfo/web-sig>`_ is the right place for
queries about WSGI in general.

For questions directly related to *twod.wsgi* or if you're not sure what's
the right place to ask a given question, please use our `2degrees-floss mailing
list <http://groups.google.com/group/2degrees-floss/>`_.


Supporting twod.wsgi
====================

If you've found this project useful, please help us spread the word about it
in the Django community!

You may also consider voting for it on
`Ohloh <https://www.ohloh.net/p/twod-wsgi>`_ and/or `Freshmeat
<http://freshmeat.net/projects/twodwsgi>`_.


Development
===========

We'll only implement the features we're going to use, but if there's something
you're missing, we'd be pleased to apply patches for the features you need, as
long as:

- They are `PEP 8 <http://www.python.org/dev/peps/pep-0008/>`_ and preferably
  `257 <http://www.python.org/dev/peps/pep-0257/>`_ compliant.
- There are unit tests for the new code.
- The new code doesn't break existing functionality.

Please go to `our development site on Bitbucket
<http://bitbucket.org/2degrees/twod.wsgi/>`_ to get the 
`latest code <http://bitbucket.org/2degrees/twod.wsgi/src/>`_,
`create branches <http://bitbucket.org/2degrees/twod.wsgi/fork/>`_
(and ask us to merge them into ours)
and raise `issues <http://bitbucket.org/2degrees/twod.wsgi/issues/>`_.


twod.wsgi versus...
===================

There are a few projects with similar aims and although *twod.wsgi* is the
newest of all, it's the only one that is both comprehensively tested and 
fully documented. We're also not aware of any production site using one of
them (there may be, though), while *twod.wsgi* has been in use at least in a
`high-traffic Web site <http://www.2degreesnetwork.com/>`_.

They all aim to implement different things. *twod.wsgi* implements them all,
and more.


repoze.django
-------------

It only implements a PasteDeploy application factory which sets the
:envvar:`DJANGO_SETTINGS_MODULE` variable, but doesn't pass the options on to
the Django settings. It's not under active development.

However, if that's all you want, it should be good enough. If you decide to
switch to *twod.wsgi* later, it'd be a piece of cake.


http-wsgi-improvements
----------------------

It's an unfinished Django branch and it's not under active development.


django_wsgi
-----------

It only allows you to run WSGI applications from Django views and also run a
set of Django views as an standalone WSGI application. We tried to join forces
and contribute to that project instead of starting this one, but never got
a response back.

We're also not sure if it's usable:

- When you run a WSGI application, the path that has been consumed by the view
  is not moved to the ``SCRIPT_NAME``. Every embedded application should
  misbehave.
- Authentication information is not passed on to the embedded application
  (i.e., ``REMOTE_USER``).
- We don't see the point in running Django views as WSGI applications. It's
  also inconvenient because no Django middleware gets run, neither do routines
  set by Django's WSGI handler. [#standalone-django]_

Although these may be bugs, not the intended behaviour.


.. rubric:: Footnotes

.. [#standalone-django] If you really wanted to collect individual views into
  an standalone Django-powered WSGI application, a safer approach would be to:
  
  #. Define the ``URLConf`` for that application (say, at ``your_package.urls_subset``).
  #. Extend the existing PasteDeploy configuration for the main/complete
     application, like this:
    
    .. code-block:: ini
    
        [app:standalone_subset]
        use = existing_main_application
        ROOT_URLCONF = your_package.urls_subset
        
  #. Use the "standalone_subset" version of your application::
  
      from paste.deploy import loadapp
      
      smaller_app = loadapp("config:/path/to/config.ini#standalone_subset")

