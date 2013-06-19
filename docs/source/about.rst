===================
About **twod.wsgi**
===================

*twod.wsgi* has only one goal, which is to bring WSGI support to Django
to the same level as in the other modern Python frameworks. We tried it to
implement these improvements at the core of Django, but unfortunately `that
is not going to happen
<http://groups.google.com/group/django-developers/browse_thread/thread/08c7ffeee7b9343c>`_
for the time being.

This is another project brought to you by `2degrees Limited
<http://dev.2degreesnetwork.com>`_.


Getting help
============

Keep in mind that **twod.wsgi is a thin integration layer**, so if you have
questions about the 3rd party software mentioned in this documentation, it's
best to use the support channels for the corresponding project.

For questions about WebOb, WebTest, PasteDeploy, PasteScript and Paste itself,
use the `paste-users mailing list <http://groups.google.com/group/paste-users>`_.
`Python's Web-SIG <http://mail.python.org/mailman/listinfo/web-sig>`_ is the
right place for queries about WSGI in general.

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

Please go to `our development site on GitHub
<https://github.com/2degrees/twod.wsgi/>`_ to get the 
`latest code <https://github.com/2degrees/twod.wsgi/download/>`_,
fork it (and ask us to merge them into ours) and raise
`issues <https://github.com/2degrees/twod.wsgi/issues/>`_.
