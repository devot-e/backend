"""
URL configuration for synd_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import re_path
from first_app import views
from django.urls import include
urlpatterns = [
    # re_path(r'^$', views.index),
    re_path(r'^first_app/',include('first_app.urls')),
    re_path('admin/', admin.site.urls),
    re_path(r'file/$', views.main),
    re_path(r'generate/', views.generate_data),
    re_path(r'sample/', views.sample_model)
]
