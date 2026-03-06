from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from ..models.door import WoodStock, Design, PanelType, EdgeProfile, PanelRise, Style
from ..forms import GenericItemForm
from .common import render_form_with_errors

def settings(request):
    """
    View to render the main settings page.
    """
    return render(request, 'settings/settings.html', {
        'title': 'Settings'
    })

def door_settings(request):
    """
    View to render the door settings page with WoodStock, Design, PanelType, EdgeProfile, PanelRise and Style data.
    """
    # Retrieve all WoodStock entries
    wood_stocks = WoodStock.objects.all().order_by('name')
    
    # Retrieve all Design entries
    designs = Design.objects.all().order_by('name')
    
    # Retrieve all PanelType entries
    panel_types = PanelType.objects.all().order_by('name')
    
    # Retrieve all EdgeProfile entries
    edge_profiles = EdgeProfile.objects.all().order_by('name')
    
    # Retrieve all PanelRise entries
    panel_rises = PanelRise.objects.all().order_by('name')
    
    # Retrieve all Style entries
    styles = Style.objects.all().order_by('name')
    
    return render(request, 'settings/door_settings.html', {
        'title': 'Door Settings',
        'wood_stocks': wood_stocks,
        'designs': designs,
        'panel_types': panel_types,
        'edge_profiles': edge_profiles,
        'panel_rises': panel_rises,
        'styles': styles
    })

def drawer_settings(request):
    """
    View to render the drawer settings page.
    """
    return render(request, 'settings/drawer_settings.html', {
        'title': 'Drawer Settings'
    })

def generic_item_form(request):
    """
    View to render the generic item form for adding miscellaneous items to an order.
    """
    form = GenericItemForm()
    return render(request, 'order/partials/generic_form.html', {
        'form': form
    })

@require_http_methods(["POST"])
def add_generic_item(request):
    """
    View to handle adding a generic/miscellaneous item.
    Receives payload with item specifications and adds to session-based order.
    """
    form = GenericItemForm(request.POST)

    if not request.session.get("current_order"):
        return render_form_with_errors(request, form, 'other', 'Please select a customer first.')

    if not form.is_valid():
        return render_form_with_errors(request, form, 'other')

    cleaned_data = form.cleaned_data
    name = cleaned_data['name']
    quantity = cleaned_data['quantity']
    price_per_unit = cleaned_data['price_per_unit']
    total_price = (price_per_unit * quantity).quantize(Decimal('0.01'))

    generic_item = {
        'type': 'other',
        'name': name,
        'quantity': str(quantity),
        'price_per_unit': str(price_per_unit.quantize(Decimal('0.01'))),
        'total_price': str(total_price)
    }

    if 'items' not in request.session['current_order']:
        request.session['current_order']['items'] = []

    edit_index = request.POST.get('edit_index')
    if edit_index is not None and edit_index != '':
        idx = int(edit_index)
        items = request.session['current_order']['items']
        if 0 <= idx < len(items):
            items[idx] = generic_item
        else:
            items.append(generic_item)
    else:
        request.session['current_order']['items'].append(generic_item)
    request.session.modified = True

    return render(request, 'door/line_items_table.html', {
        'items': request.session['current_order']['items']
    })
