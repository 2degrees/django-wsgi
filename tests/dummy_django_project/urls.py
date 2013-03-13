from django.conf.urls import patterns
from django.http import HttpResponse


urlpatterns = patterns(
    '',
    ('^$', lambda request: HttpResponse()),
    )
