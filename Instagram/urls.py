from django.urls import path
from . import views


urlpatterns = [

    path('', views.home, name= 'home'),
    path('token/', views.token, name='token'),

]


from django.views.generic import RedirectView
urlpatterns += [
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
]
