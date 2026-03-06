from django.urls import path
from ..views import drawer_form, add_drawer
from ..views.drawer import calculate_drawer_price

urlpatterns = [
    path('form/', drawer_form, name='drawer_form'),
    path('add/', add_drawer, name='new_drawer'),
    path('calculate-price/', calculate_drawer_price, name='calculate_drawer_price'),
] 