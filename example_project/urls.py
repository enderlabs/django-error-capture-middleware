from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin


admin.autodiscover()
urlpatterns = patterns('')

# If we are set to debug, go ahead and serve static media
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^simple/media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': '../src/django_error_capture_middleware/media/'}),
    )


urlpatterns += patterns('',
    # Example item that will throw a trace
    (r'^a/', 'asd'),
    # SimpleTicket application
    (r'^simple/', include('django_error_capture_middleware.urls')),
    # Django administration
    (r'^admin/', include(admin.site.urls)),
)
