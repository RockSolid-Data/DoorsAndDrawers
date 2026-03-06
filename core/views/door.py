from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from ..forms import DoorForm
from ..models.door import DoorLineItem, WoodStock, Style, PanelRise
from .common import process_line_item_form, get_current_customer
from ..models import Customer
from ..services.door_defaults_service import DoorDefaultsService

@require_http_methods(["GET", "POST"])
def door_form(request):
    """
    View to handle the door form.
    GET: Returns the form template
    POST: Processes the form data
    """
    # Initial data for the form
    initial_data = {}
    
    # Check if we have a customer in the session
    customer = get_current_customer(request)
    
    # If we have a customer, get their defaults
    if customer:
        door_defaults_service = DoorDefaultsService()
        initial_data = door_defaults_service.apply_defaults_to_form(customer)

    # Process the form
    if request.method == 'POST':
        form = DoorForm(request.POST, initial=initial_data)
        if form.is_valid():
            return process_line_item_form(request, form, 'door')
    else:
        form = DoorForm(initial=initial_data)

    return render(request, 'door/door_form.html', {
        'form': form,
        'title': 'Add Door'
    })

def transform_door_data(request, cleaned_data, door_model, item_type, custom_price, price):
    """Transform door form data to session format"""
    # Get customer defaults if available
    customer = get_current_customer(request)
    door_defaults_service = DoorDefaultsService()
    
    # Get interior rail size from customer defaults or global defaults
    interior_rail_size = door_defaults_service.get_rail_size(
        customer, 
        'interior_rail_size'
    ) if customer else door_defaults_service.global_defaults['interior_rail_size']

    return {
        'type': item_type,
        'wood_stock': {'id': cleaned_data['wood_stock'].pk, 'name': cleaned_data['wood_stock'].name},
        'edge_profile': {'id': cleaned_data['edge_profile'].pk, 'name': cleaned_data['edge_profile'].name},
        'panel_rise': {'id': cleaned_data['panel_rise'].pk, 'name': cleaned_data['panel_rise'].name},
        'style': {'id': cleaned_data['style'].pk, 'name': str(cleaned_data['style'])},
        'width': str(cleaned_data['width']),
        'height': str(cleaned_data['height']),
        'quantity': str(cleaned_data['quantity']),
        'price_per_unit': str(door_model.price_per_unit.quantize(Decimal('0.01'))),
        'total_price': str(price.quantize(Decimal('0.01'))),
        'rail_top': str(cleaned_data['rail_top']),
        'rail_bottom': str(cleaned_data['rail_bottom']),
        'rail_left': str(cleaned_data['rail_left']),
        'rail_right': str(cleaned_data['rail_right']),
        'interior_rail_size': str(interior_rail_size),
        'custom_price': custom_price
    }

@require_http_methods(["POST"])
def add_door(request):
    """
    View to handle adding a door.
    Receives payload with door specifications and adds to session-based order.
    """
    return process_line_item_form(
        request, 
        DoorForm, 
        DoorLineItem, 
        'door',
        transform_door_data
    )

@require_http_methods(["GET"])
def calculate_door_price(request):
    """Return calculated price breakdown for a door given current form values."""
    try:
        wood_stock_id = request.GET.get('wood_stock')
        style_id = request.GET.get('style')
        panel_rise_id = request.GET.get('panel_rise')
        width = request.GET.get('width')
        height = request.GET.get('height')
        quantity = request.GET.get('quantity', '1')

        if not all([wood_stock_id, style_id, width, height]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        wood_stock = WoodStock.objects.get(pk=wood_stock_id)
        style = Style.objects.get(pk=style_id)
        panel_rise = PanelRise.objects.get(pk=panel_rise_id) if panel_rise_id else None

        item = DoorLineItem(
            wood_stock=wood_stock,
            style=style,
            panel_rise=panel_rise,
            width=Decimal(width),
            height=Decimal(height),
            quantity=int(quantity),
        )
        price_per_unit = item.calculate_price()
        qty = int(quantity)
        total = (price_per_unit * qty).quantize(Decimal('0.01'))

        return JsonResponse({
            'price_per_unit': str(price_per_unit),
            'total': str(total),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def get_current_customer(request):
    """
    Get the current customer from session or order
    
    Args:
        request: HTTP request object
        
    Returns:
        Customer object or None
    """
    # If we have a current order in the session
    if 'current_order' in request.session:
        # Check for customer key in the current_order
        if 'customer' in request.session['current_order']:
            customer_id = request.session['current_order']['customer']
            try:
                return Customer.objects.get(pk=customer_id)
            except Customer.DoesNotExist:
                pass
    
    return None