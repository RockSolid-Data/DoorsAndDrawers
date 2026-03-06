from decimal import Decimal
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from ..models.drawer import (
    DrawerLineItem, DrawerWoodStock, DrawerBottomSize,
    DrawerPricing, DrawerDimensionSurcharge, DefaultDrawerSettings,
)
from ..forms import DrawerForm
from .common import process_line_item_form
from .door import get_current_customer

def drawer_form(request):
    """Render the drawer form partial template."""
    wood_stocks = DrawerWoodStock.objects.all()
    bottom_sizes = DrawerBottomSize.objects.all()
    
    # Initial data for the form
    initial_data = {}
    
    # Check if we have a customer in the session
    customer = get_current_customer(request)
    
    # If we have a customer, get their defaults
    if customer:
        drawer_defaults = customer.get_drawer_defaults()
        
        # Apply known defaults from JSON
        if 'wood_stock' in drawer_defaults:
            try:
                wood_stock_id = drawer_defaults['wood_stock']
                if isinstance(wood_stock_id, (int, str)):  # Ensure we have an ID
                    initial_data['wood_stock'] = DrawerWoodStock.objects.get(pk=wood_stock_id)
            except (DrawerWoodStock.DoesNotExist, ValueError, TypeError):
                pass
                
        if 'bottom' in drawer_defaults:
            try:
                bottom_id = drawer_defaults['bottom']
                if isinstance(bottom_id, (int, str)):  # Ensure we have an ID
                    initial_data['bottom'] = DrawerBottomSize.objects.get(pk=bottom_id)
            except (DrawerBottomSize.DoesNotExist, ValueError, TypeError):
                pass
        
        # Apply boolean options
        for option in ['undermount', 'finishing']:
            if option in drawer_defaults:
                initial_data[option] = drawer_defaults[option]
    
    # Create form with initial data
    form = DrawerForm(initial=initial_data)
    
    context = {
        'form': form,
        'wood_stocks': wood_stocks,
        'bottom_sizes': bottom_sizes,
    }
    
    return render(request, 'drawer/drawer_form.html', context)

def transform_drawer_data(request, cleaned_data, drawer_model, item_type, custom_price, price):
    """Transform drawer form data to session format"""
    return {
        'type': item_type,
        'wood_stock': {'id': cleaned_data['wood_stock'].pk, 'name': cleaned_data['wood_stock'].name},
        'bottom': {'id': cleaned_data['bottom'].pk, 'name': cleaned_data['bottom'].name},
        'width': str(cleaned_data['width']),
        'height': str(cleaned_data['height']),
        'depth': str(cleaned_data['depth']),
        'quantity': str(cleaned_data['quantity']),
        'undermount': cleaned_data['undermount'],
        'finishing': cleaned_data['finishing'],
        'price_per_unit': str(drawer_model.price_per_unit.quantize(Decimal('0.01'))),
        'total_price': str(price.quantize(Decimal('0.01'))),
        'custom_price': custom_price
    }

@require_http_methods(["POST"])
def add_drawer(request):
    """
    View to handle adding a drawer.
    Receives payload with drawer specifications and adds to session-based order.
    """
    return process_line_item_form(
        request, 
        DrawerForm, 
        DrawerLineItem, 
        'drawer',
        transform_drawer_data
    )


@require_http_methods(["GET"])
def calculate_drawer_price(request):
    """Return calculated price breakdown for a drawer given current form values.
    
    Returns base_price (before surcharge), surcharge_percent, price_per_unit, and total.
    """
    try:
        wood_stock_id = request.GET.get('wood_stock')
        bottom_id = request.GET.get('bottom')
        width = request.GET.get('width')
        height = request.GET.get('height')
        depth = request.GET.get('depth')
        undermount = request.GET.get('undermount', '0') == '1'
        finishing = request.GET.get('finishing', '0') == '1'
        quantity = request.GET.get('quantity', '1')

        if not all([wood_stock_id, bottom_id, width, height, depth]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        wood_stock = DrawerWoodStock.objects.get(pk=wood_stock_id)
        bottom = DrawerBottomSize.objects.get(pk=bottom_id)
        w = Decimal(width)
        h = Decimal(height)
        d = Decimal(depth)

        tier = DrawerPricing.objects.filter(height__gte=h).order_by('height').first()
        if tier is None:
            tier = DrawerPricing.objects.order_by('-height').first()
        tier_price = tier.price if tier else Decimal('0.00')

        base_price = tier_price + wood_stock.price + bottom.price

        default_settings = DefaultDrawerSettings.objects.first()
        if default_settings:
            if undermount:
                base_price += default_settings.undermount_charge
            if finishing:
                base_price += default_settings.finish_charge

        matching = DrawerDimensionSurcharge.objects.filter(
            Q(width__gt=0, width__lte=w) | Q(depth__gt=0, depth__lte=d)
        ).order_by('-surcharge_percent').first()

        surcharge_percent = matching.surcharge_percent if matching else Decimal('0.00')
        price_per_unit = (base_price * (1 + surcharge_percent / Decimal('100'))).quantize(Decimal('0.01'))
        qty = int(quantity)
        total = (price_per_unit * qty).quantize(Decimal('0.01'))

        return JsonResponse({
            'base_price': str(base_price.quantize(Decimal('0.01'))),
            'surcharge_percent': str(surcharge_percent),
            'price_per_unit': str(price_per_unit),
            'total': str(total),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400) 