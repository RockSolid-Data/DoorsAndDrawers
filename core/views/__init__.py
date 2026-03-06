from django.shortcuts import render
from .customer import (
    customers, new_customer,
    edit_customer, delete_customer
)
from .order import (
    orders, edit_order, create_order,
    delete_order, get_line_item, convert_to_order
)
from .quote import (
    quotes,
)
from .line_item import (
    settings, door_settings, drawer_settings,
    generic_item_form
)
from .door import (
    door_form, add_door
)
from .drawer import (
    drawer_form, add_drawer
)
from . import common
from . import lifecycle

def home(request):
    return render(request, 'home.html', {
        'title': 'Home'
    })

__all__ = [
    'home',
    'customers', 'new_customer',
    'edit_customer', 'delete_customer',
    'orders', 'edit_order', 'create_order',
    'delete_order', 'convert_to_order',
    'quotes',
    'settings', 'door_settings', 'drawer_settings',
    'door_form', 'drawer_form', 'add_drawer',
    'common',
]
