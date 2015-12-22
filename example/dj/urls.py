from django.conf import settings
from django.conf.urls import include, patterns, url

from is_core.site import site

from ats_sms_operator.cores.resources import InputATSSMSmessageResource


urlpatterns = patterns(
    '',
    url(r'^', include(site.urls)),
    url(r'^api/atsinputsmsmessage/$', InputATSSMSmessageResource.as_view(callback_function=lambda x, y: x)),
)

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
