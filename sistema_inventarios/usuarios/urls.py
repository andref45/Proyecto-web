from django.urls import path
from . import views

urlpatterns = [
    path('', views.iniciar_sesion, name='login'),
    path('registro/', views.registro, name='registro'),
    path('home/', views.home, name='home'),

]