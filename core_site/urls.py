from django.contrib import admin
from django.urls import path, include
from django.conf import settings # <-- NEW
from django.conf.urls.static import static # <-- NEW

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
]

# <-- NEW: This tells Django how to serve the images to the browser
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)