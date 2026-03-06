from django.urls import path
from ..views import door_form, add_door
from ..views.door import calculate_door_price

urlpatterns = [
    path('form/', door_form, name='door_form'),
    path('add/', add_door, name='new_door'),
    path('calculate-price/', calculate_door_price, name='calculate_door_price'),
] 