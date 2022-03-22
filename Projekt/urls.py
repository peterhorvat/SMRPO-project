"""Projekt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework import routers
from website import views as v

router = routers.DefaultRouter(trailing_slash=False)
# router.register(r'apiExample/$', v.viewExample, 'viewExample')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', v.landing_page, name='landing_page'),
    path('login/', v.login_page, name='login_page'),
    path("create_new_project/", v.create_new_project, name='create_new_project'),
    path("delete_project/<int:id>", v.delete_project, name='delete_project'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('createOTP/', v.createOTP, name='createOTP'),
    path('disableOTP/', v.disableOTP, name='disableOTP'),
    path('loginOTP/', v.loginOTP, name='loginOTP'),
    path('projects/<int:project_id>/', v.project_page, name = 'project_page'),
    path('projects/<int:project_id>/stories/new/', v.new_story, name='create_story'),
]