"""
URL configuration for HH project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# backend/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from jobseekers.views import ResumeViewSet, ApplicationViewSet
from employers.views import VacancyViewSet
from messenger.views import ChatRoomViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'jobseekers/resumes', ResumeViewSet)
router.register(r'jobseekers/applications', ApplicationViewSet)
router.register(r'employers/vacancies', VacancyViewSet)
router.register(r'messenger/chatrooms', ChatRoomViewSet)
router.register(r'messenger/messages', MessageViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('ws/', include('messenger.routing.websocket_urlpatterns')),
]