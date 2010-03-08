============================
Custom status reason phrases
============================

According to the `HTTP specification
<http://www.w3.org/Protocols/rfc2616/rfc2616-sec6.html#sec6.1.1>`_, the reason
phrase for an HTTP response status may be customised, so you could return
``200 Alright then`` or ``403 Get out``. However, `Django doesn't support this
<http://code.djangoproject.com/ticket/12747>`_, so *twod.wsgi* provides a
subclass of :class:`~django.http.HttpResponse` which does allow custom response
reasons, since they could be returned by :doc:`embedded WSGI applications
<embedded-apps>`.

If you want to use it in your Django views, just use it like a regular Django
response, but include the phrase in the ``status`` argument::

    from twod.wsgi import TwodResponse
    
    response = TwodResponse("You cannot be here", mimetype="text/plain", status="403 Get out")

For this to work, you'd need to use the :doc:`enhanced Django handler
<request-objects>`.
