=========================
Routing arguments support
=========================

`routing_args <http://wsgi.org/wsgi/Specifications/routing_args>`_ is an
extension to the WSGI standard which normalises the place to put the
arguments found in the URL. This is particularly useful for 3rd party WSGI
libraries and the dispatching components in Web frameworks
are expected to set it, but Django does not: Therefore we created the
:class:`twod.wsgi.RoutingArgsMiddleware` Django middleware.

If you requested the path ``/blog/posts/hello-world/comments/3``, then the
arguments ``hello-world`` and ``3`` will be available in the request object.
Depending on how you defined your URL patterns, they'll be a dictionary (if you
used named groups) or a tuple (if you didn't set names for the matching groups).
The former are referred to as "named arguments" and the later as "positional
arguments" in .
