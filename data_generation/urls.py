from django.urls import re_path
from data_generation import views

urlpatterns= [
    re_path(r'file/$', views.main),
    re_path(r'generate/', views.generate_data),
    re_path(r'sample/', views.sample_model),
    re_path(r'report/', views.generate_report)
]