===========================
Embedding WSGI applications
===========================

The other WSGI frameworks support running external applications from within
the current WSGI application and Django does now thanks to *twod.wsgi*. This
gives you the ability to serve 3rd party applications on-the-fly, as well as
control the requests they get and the responses they return (in order to
filter them or replace them completely).

Nearly all the Python Web applications out there have built-in WSGI support,
including well-known projects like `Trac <http://trac.edgewall.org/>`_ and
`Mercurial <http://mercurial.selenic.com/>`_. So you'll be able to integrate
them nicely into your Django application, to support Single Sign-On or manage
authorisation, for example -- **Everything would be controlled from your own
application**.

These WSGI applications can also be Web applications written in a programming
language other than Python, since there are WSGI applications which run other
Web applications as a Web server/gateway would do it (e.g.,
:class:`paste.cgiapp.CGIApplication` for CGI scripts).

Regardless of the technology used by the embedded application, you will always
pass a Django request object and receive a Django response object. As a
consequence, you must be using the :doc:`enhanced request objects
<request-objects>`.


.. note::

    Django people distinguish "projects" from "applications". From a WSGI
    point of view, those so-called "Django projects" are "WSGI applications"
    and the so-called "Django applications" are just a framework-specific thing
    with no equivalent.
    
    To keep things simple while using the right WSGI terminology,
    Django-powered WSGI applications are referred to as "Django applications"
    within this documentation.


Embedding non-Django applications
=================================

You can mount WSGI applications directly in your Django URL configuration, or
call them from a view to filter the requests they get and/or the response they
return.


Mounting them as Django views
-----------------------------

You just need to load an instance for that application and put it in your
``URLConf``, like this::

    # urls.py
    
    from twod.wsgi import make_wsgi_view
    from cool_wsgi_app import CoolApplication
    
    urlpatterns = patterns('',
      # ...
      (r'^cool-application(/.*)$', make_wsgi_view(CoolApplication())),
      # ...
    )

Note the path to be consumed by this application must be captured by the
regular expression. If you want to give it a name, use ``path_info``.

When called, this application will get the same request your view received. So,
among other things, if the user is logged in in Django, he will be also be
logged in in the inner WSGI application (as long as it takes the ``REMOTE_USER``
variable into account).

.. attention::
    The path to be consumed by the embedded WSGI application must be the last
    portion of the original ``PATH_INFO``. Your own application can only consume
    the beginning of such a path. So you won't be able to do something like::
    
        (r'^cool-application(/.*)/foo$', make_wsgi_view(CoolApplication()))


Calling them from a Django view
-------------------------------

If you need more control over what the inner application receives and/or what it
returns, you'd need to call it yourself from your view by using
:func:`twod.wsgi.call_wsgi_app`.

Say you want to serve an instance of `Trac <http://trac.edgewall.org/>`_ and
you need to set the path to the Trac environment on a per request basis
(because you're hosting multiple Trac instances). You would create the
following Django view::

    from twod.wsgi import call_wsgi_app
    from trac.web.main import dispatch_request as trac
    
    def run_trac(request, path_info):
        request.environ['trac.env_path'] = "path/to/trac/env"
        return call_wsgi_app(trac, request, path_info)

If you then want to make it use your existing login and logout forms, you
can update the view to make it look like this::

    from django.shortcuts import redirect
    from twod.wsgi import call_wsgi_app
    from trac.web.main import dispatch_request as trac
    
    def run_trac(request, path_info):
        
        if path_info.startswith("/login"):
            return redirect("/my-login-form")
        if path_info.startswith("/logout"):
            return redirect("/my-logout-form")
        
        request.environ['trac.env_path'] = "path/to/trac/env"
        return call_wsgi_app(trac, request, path_info)

And if you're even more ambitious and want to serve Trac instances on-the-fly,
you'd do this::

    from django.shortcuts import redirect
    from twod.wsgi import call_wsgi_app
    from trac.web.main import dispatch_request as trac
    
    def run_trac(request, trac_id, path_info):
        
        if path_info.startswith("/login"):
            return redirect("/my-login-form")
        if path_info.startswith("/logout"):
            return redirect("/my-logout-form")
        
        request.environ['trac.env_path'] = "/var/trac-instances/%s" % trac_id
        return call_wsgi_app(trac, request, path_info)
    
    
    # urls.py
    
    urlpatterns = patterns('',
      # ...
      (r'^tracs/(?<trac_id>\w+)(?<path_info>/.*)$', "yourpackage.views.run_trac"),
      # ...
    )


Modifying the response
~~~~~~~~~~~~~~~~~~~~~~

As we mentioned above, you can deal with the response given by the WSGI
application, which is available as a :class:`django.http.HttpResponse` instance.

You can do anything you want with the response before returning it. If, for
example, you wanted to set the ``Server`` header, you could do it like this::

    from twod.wsgi import call_wsgi_app
    from somewhere import wsgi_app
    
    def run_app(request, path_info):
        response = call_wsgi_app(wsgi_app, request, path_info)
        response['Server'] = "twod.wsgi 1.0"
        return response

.. warning:: **Avoid reading the body of a request!**
    
    The body of some responses may be generators, which are useful when the
    response is so big that has to be sent in chunks (e.g., a video).
    If you read their body, you would consume it and thus you would also alter
    the status of said body.
    
    If you do need to read it, check the ``Content-Type`` first to make sure
    that's what you're looking for. If it really is, and the body is a
    generator, make sure to pass on a proper response body.
    
    Note it's absolutely fine to deal with the response status and headers,
    though.
