from django.urls import path
from ..views.customer import customers, new_customer, edit_customer, delete_customer, customer_search

urlpatterns = [
    path('', customers, name='customers'),
    path('create/', new_customer, name='new_customer'),
    path('<int:customer_id>/', edit_customer, name='edit_customer'),
    path('<int:customer_id>/delete/', delete_customer, name='delete_customer'),
    path('search/', customer_search, name='customer_search'),
] 