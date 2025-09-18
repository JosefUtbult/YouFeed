from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('update', views.update, name='update'),
    path('register_viewed', views.register_viewed, name='register_viewed')
]


