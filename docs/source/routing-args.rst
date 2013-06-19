=========================
Routing arguments support
=========================

`routing_args <http://wsgi.org/wsgi/Specifications/routing_args>`_ is an
extension to the WSGI standard which normalises the place to put the
arguments found in the URL. This is particularly useful for 3rd party WSGI
libraries and the dispatching components in Web frameworks
are expected to set it, but Django does not: Therefore we created the
:class:`~twod.wsgi.RoutingArgsMiddleware` Django middleware.

If you requested the path ``/blog/posts/hello-world/comments/3``, then the
arguments ``hello-world`` and ``3`` will be available in the request object.
Depending on how you defined your URL patterns, they'll be a dictionary (if you
used named groups) or a tuple (if you didn't set names for the matching groups).
The former are referred to as "named arguments" and the latter as "positional
arguments" in *routing_args* specification.

:class:`~twod.wsgi.RoutingArgsMiddleware` simply puts the arguments found by the
Django URL resolver in the ``request`` object. It's such a simple thing, but
it's key for Django-independent libraries, which may not be run in the
context of a Django middleware nor a Django view.


Named arguments
===============

The named arguments for the request are available at ``request.urlvars``, an
attribute provided by :doc:`WebOb <request-objects>`.

So, if you had the following URL pattern::

    (r'^/blog/posts/(?<post_slug>\w+)/comments/(?<post_comment_id>\d+)$', post_comment)

a request may have the following named arguments::

    >>> request.urlvars
    {'post_slug': "hello-world", 'post_comment_id': "3"}


Positional arguments
====================

The positional arguments for the request are available at ``request.urlargs``,
another attribute provided by :doc:`WebOb <request-objects>`.

If you had the following URL pattern::

    (r'^/blog/posts/(\w+)/comments/(\d+)$', post_comment)

a request may have the following named arguments::

    >>> request.urlvars
    ("hello-world", "3")
