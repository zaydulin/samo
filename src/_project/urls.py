from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    #path("__debug__/", include("debug_toolbar.urls")),
    path("_nested_admin/", include("nested_admin.urls")),
    path('developer_management/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),

]

urlpatterns += [
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('tinymce/', include('tinymce.urls')),
]

urlpatterns += i18n_patterns(
path('', include('webmain.urls')),
    path('', include('useraccount.urls')),
    path('', include('moderation.urls')),
    path('', include('conference.urls')),
)
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path('rosetta/', include('rosetta.urls'))
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)