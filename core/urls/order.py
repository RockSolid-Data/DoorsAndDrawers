from django.urls import path
from ..views.order import (
    orders, edit_order, create_order, delete_order, convert_to_order,
    get_customer_details, order_search, remove_line_item, confirm_remove_line_item,
    get_line_item, generate_order_pdf, print_modal, print_documents
)

urlpatterns = [
    path('', orders, name='orders'),
    path('create/', create_order, name='new_order'),
    path('<int:order_id>/', edit_order, name='edit_order'),
    path('<int:order_id>/delete/', delete_order, name='delete_order'),
    path('<int:order_id>/convert/', convert_to_order, name='convert_to_order'),
    path('<int:order_id>/pdf/', generate_order_pdf, name='order_pdf'),
    path('<int:order_id>/print-modal/', print_modal, name='print_modal'),
    path('<int:order_id>/print/', print_documents, name='print_documents'),
    path('get-customer-address/', get_customer_details, name='get_customer_address'),
    path('search/', order_search, name='order_search'),
    path('items/<int:item_id>/data/', get_line_item, name='get_line_item'),
    path('items/<int:item_id>/remove/', remove_line_item, name='remove_line_item'),
    path('items/<int:item_id>/confirm-remove/', confirm_remove_line_item, name='confirm_remove_line_item'),
] 