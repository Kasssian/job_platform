from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', include('core_models.urls', namespace='core')),
    path('jobseekers/', include('jobseekers.urls', namespace='jobseekers')),
    path('employers/', include('employers.urls', namespace='employers')),
    path('messages/', include('messenger.urls', namespace='messenger')),
    
    path('accounts/', include('django.contrib.auth.urls')),  # logout, password_change и т.д.
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)