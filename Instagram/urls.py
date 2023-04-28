from django.urls import path
from . import views


urlpatterns = [

    path('', views.home, name= 'home'),
    path('token/', views.token, name='token'),
    path('api/test/', views.get_messages, name='hello')

]

