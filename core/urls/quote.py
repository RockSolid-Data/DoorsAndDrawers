from django.urls import path
from ..views.quote import quotes, quote_search

urlpatterns = [
    path('', quotes, name='quotes'),
    path('search/', quote_search, name='quote_search'),
]
