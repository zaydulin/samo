from django.urls import path, include

urlpatterns = [
    path('', include(('webmain.urls', 'webmain'), namespace='webmain')),
    # Add other URL patterns or includes as needed
]