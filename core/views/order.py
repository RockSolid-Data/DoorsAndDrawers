import io

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.template.loader import render_to_string
from django.urls import reverse
from xhtml2pdf import pisa

from ..forms import OrderForm
from ..models import Order, DoorLineItem
from django.http import HttpResponse, JsonResponse
from ..models.customer import Customer
from ..models.door import DoorLineItem
from itertools import chain
from ..services.order_service import OrderService
from .common import handle_entity_search, handle_entity_list


def _entity_label(is_quote):
    return 'Quote' if is_quote else 'Order'


def _list_url_name(is_quote):
    return 'quotes' if is_quote else 'orders'


def orders(request):
    """List all confirmed orders with pagination."""
    return handle_entity_list(
        request,
        Order.confirmed.all().select_related('customer'),
        'order/orders.html',
        'orders',
        'Orders'
    )

def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    is_quote = order.is_quote
    label = _entity_label(is_quote)
    edit_ctx = {
        'editing': True,
        'order': order,
        'form_action': reverse('edit_order', args=[order.id]),
        'is_quote': is_quote,
    }

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            session_data = request.session.get('current_order', {})
            items = session_data.get('items', [])

            if not items:
                messages.error(request, "You need to add at least one item.")
                return render(request, 'order/order_form.html', {
                    'form': form, 'title': f'Edit {label} {order.order_number}',
                    'items': items, **edit_ctx,
                }, status=422)

            success, order, error = OrderService.update_from_session(
                order, form.cleaned_data, session_data
            )

            if success:
                if 'current_order' in request.session:
                    del request.session['current_order']
                    request.session.modified = True
                messages.success(request, f'{label} updated successfully!')
                if request.POST.get('action') == 'save_and_print':
                    url = reverse('edit_order', args=[order.id]) + '?print=1'
                else:
                    url = reverse('quotes' if is_quote else 'orders')
                return redirect(url)
            else:
                messages.error(request, error)
                return render(request, 'order/order_form.html', {
                    'form': form, 'title': f'Edit {label} {order.order_number}',
                    'items': items, **edit_ctx,
                }, status=422)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f"{form[field].label}: {error}")
            session_data = request.session.get('current_order', {})
            return render(request, 'order/order_form.html', {
                'form': form, 'title': f'Edit {label} {order.order_number}',
                'items': session_data.get('items', []), **edit_ctx,
            }, status=422)

    session_data = OrderService.serialize_to_session(order)
    request.session['current_order'] = session_data
    request.session.modified = True

    form = OrderForm(instance=order)
    return render(request, 'order/order_form.html', {
        'form': form,
        'title': f'Edit {label} {order.order_number}',
        'items': session_data['items'],
        **edit_ctx,
    })

def create_order(request):
    is_quote = request.GET.get('is_quote') == '1' if request.method == 'GET' else False
    label = _entity_label(is_quote)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            is_quote = form.cleaned_data.get('is_quote', False)
            label = _entity_label(is_quote)

            session_data = request.session.get('current_order', {})
            items = session_data.get('items', [])

            if not items:
                messages.error(request, f"You need to add at least one item to create a {label.lower()}.")
                return render(request, 'order/order_form.html', {
                    'form': form, 'title': f'Create {label}', 'is_quote': is_quote,
                }, status=422)

            if 'customer' not in session_data:
                messages.error(request, f"Please select a customer for this {label.lower()}.")
                return render(request, 'order/order_form.html', {
                    'form': form, 'title': f'Create {label}', 'is_quote': is_quote,
                }, status=422)

            success, order, error = OrderService.create_from_session(
                form.cleaned_data,
                session_data,
                is_quote=is_quote
            )

            if success:
                if 'current_order' in request.session:
                    del request.session['current_order']
                    request.session.modified = True

                messages.success(request, f'{label} created successfully!')
                if request.POST.get('action') == 'save_and_print':
                    url = reverse('edit_order', args=[order.id]) + '?print=1'
                else:
                    url = reverse('quotes' if is_quote else 'orders')
                return redirect(url)
            else:
                if "Data integrity error" in error:
                    messages.error(request, f"There was a problem with the data. Please check all fields and try again.")
                elif "Database error" in error:
                    messages.error(request, "There was a database problem. Please try again later.")
                else:
                    messages.error(request, error)

                return render(request, 'order/order_form.html', {
                    'form': form, 'title': f'Create {label}', 'is_quote': is_quote,
                }, status=422)
        else:
            is_quote = request.POST.get('is_quote') == 'True' or request.POST.get('is_quote') == 'on'
            label = _entity_label(is_quote)
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f"{form[field].label}: {error}")

            return render(request, 'order/order_form.html', {
                'form': form, 'title': f'Create {label}', 'is_quote': is_quote,
            }, status=422)
    else:
        if 'current_order' in request.session:
            del request.session['current_order']
            request.session.modified = True

        form = OrderForm(initial={'is_quote': is_quote})

    return render(request, 'order/order_form.html', {
        'form': form,
        'title': f'Create {label}',
        'is_quote': is_quote,
    })

def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    is_quote = order.is_quote
    label = _entity_label(is_quote)
    list_url = _list_url_name(is_quote)

    if request.method == 'POST':
        order.delete()
        messages.success(request, f'{label} deleted successfully!')
        if request.headers.get('HX-Request'):
            response = HttpResponse()
            response['HX-Redirect'] = reverse(list_url)
            return response
        return redirect(list_url)

    return render(request, 'order/order_confirm_delete.html', {
        'order': order,
        'title': f'Delete {label} {order.order_number}'
    })

def convert_to_order(request, order_id):
    order = get_object_or_404(Order.quotes, id=order_id)
    if request.method == 'POST':
        order.is_quote = False
        order.save()
        messages.success(request, 'Quote converted to order successfully!')
        if request.headers.get('HX-Request'):
            response = HttpResponse()
            response['HX-Redirect'] = reverse('edit_order', args=[order.id])
            return response
        return redirect('edit_order', order_id=order.id)

    return render(request, 'order/order_convert_confirm.html', {
        'order': order,
        'title': f'Convert Quote {order.order_number} to Order'
    })

def get_customer_details(request):
    customer_id = request.GET.get('customer')
    if not customer_id:
        return JsonResponse({
            'addresses': {'address1': '', 'address2': ''},
            'defaults': {
                'discount_type': '',
                'discount_value': '',
                'surcharge_type': '',
                'surcharge_value': '',
                'shipping_type': '',
                'shipping_value': '',
                'taxable': False,
                'tax_percentage': '0',
            }
        })

    try:
        customer = Customer.objects.get(id=customer_id)
        defaults = customer.defaults if hasattr(customer, 'defaults') else None

        billing_address1 = (customer.address_line1 or '').title()
        billing_address2 = (customer.address_line2 or '').title()

        response_data = {
            'addresses': {
                'address1': billing_address1,
                'address2': billing_address2
            },
            'notes': (customer.notes or '').title(),
            'defaults': {
                'discount_type': defaults.discount_type if defaults else '',
                'discount_value': str(defaults.discount_value) if defaults else '',
                'surcharge_type': defaults.surcharge_type if defaults else '',
                'surcharge_value': str(defaults.surcharge_value) if defaults else '',
                'shipping_type': defaults.shipping_type if defaults else '',
                'shipping_value': str(defaults.shipping_value) if defaults else '',
                'taxable': customer.taxable,
                'tax_percentage': str(customer.tax_percentage),
            }
        }

        # Preserve existing items when changing customers
        existing_items = []
        if 'current_order' in request.session and 'items' in request.session['current_order']:
            existing_items = request.session['current_order']['items']

        # Update order in session with new customer data but keep existing items
        request.session['current_order'] = {
            'customer': customer_id,
            'billing_address1': billing_address1,
            'billing_address2': billing_address2,
            'items': existing_items
        }

        request.session.modified = True

        return JsonResponse(response_data)
    except (Customer.DoesNotExist, ValueError):
        return JsonResponse({
            'addresses': {'address1': '', 'address2': ''},
            'defaults': {
                'discount_type': '',
                'discount_value': '',
                'surcharge_type': '',
                'surcharge_value': '',
                'shipping_type': '',
                'shipping_value': '',
                'taxable': False,
                'tax_percentage': '0',
            }
        })

def order_search(request):
    """Search and filter orders based on criteria."""
    # Use the common search handler with order-specific parameters
    return handle_entity_search(
        request,
        Order.confirmed.all().select_related('customer'),
        'order/partials/order_results.html',
        'orders'
    )

def get_line_item(request, item_id):
    """Return session item data as JSON for editing."""
    session_data = request.session.get('current_order', {})
    items = session_data.get('items', [])
    index = int(item_id)
    if 0 <= index < len(items):
        return JsonResponse(items[index])
    return JsonResponse({'error': 'Item not found'}, status=404)

def confirm_remove_line_item(request, item_id):
    """Render confirmation modal for removing a line item."""
    from django.urls import reverse
    session_data = request.session.get('current_order', {})
    items = session_data.get('items', [])
    index = int(item_id)

    item_desc = "this item"
    if 0 <= index < len(items):
        item = items[index]
        item_type = item.get('type', 'item')
        item_desc = f"this {item_type} item"

    return render(request, 'partials/confirm_delete_modal.html', {
        'delete_title': 'Remove Line Item',
        'delete_message': f'Are you sure you want to remove {item_desc}? This action cannot be undone.',
        'delete_url': reverse('remove_line_item', args=[item_id]),
    })


def remove_line_item(request, item_id):
    """
    Remove a line item from the current order.
    Handles both database-persisted items and session-based items.
    """
    if request.method == 'DELETE':
        if 'current_order' in request.session:
            try:
                index = int(item_id)
                if 'items' in request.session['current_order'] and 0 <= index < len(request.session['current_order']['items']):
                    request.session['current_order']['items'].pop(index)
                    request.session.modified = True
                    response = render(request, 'door/line_items_table.html', {
                        'items': request.session['current_order']['items']
                    })
                    response['HX-Retarget'] = '.line-items-container'
                    response['HX-Reswap'] = 'outerHTML'
                    response['HX-Trigger-After-Swap'] = 'closeModal'
                    return response
                else:
                    return HttpResponse("Item not found in session", status=404)
            except (ValueError, IndexError):
                return HttpResponse("Invalid item index", status=400)

        order_id = request.session.get('order_id')
        if not order_id:
            return HttpResponse("No active order", status=400)

        order = get_object_or_404(Order, id=order_id)
        item_removed = False

        if hasattr(order, 'door_items'):
            door_item = order.door_items.filter(id=item_id).first()
            if door_item:
                door_item.delete()
                item_removed = True

        if not item_removed and hasattr(order, 'drawer_items'):
            drawer_item = order.drawer_items.filter(id=item_id).first()
            if drawer_item:
                drawer_item.delete()
                item_removed = True

        if not item_removed:
            return HttpResponse("Item not found", status=404)

        if hasattr(order, 'line_items') and callable(getattr(order, 'line_items')):
            items = order.line_items
        else:
            door_items_list = list(order.door_items.all()) if hasattr(order, 'door_items') else []
            drawer_items_list = list(order.drawer_items.all()) if hasattr(order, 'drawer_items') else []
            items = list(chain(door_items_list, drawer_items_list))

        response = render(request, 'door/line_items_table.html', {'items': items})
        response['HX-Retarget'] = '.line-items-container'
        response['HX-Reswap'] = 'outerHTML'
        response['HX-Trigger-After-Swap'] = 'closeModal'
        return response

    return redirect('orders')


def generate_order_pdf(request, order_id):
    """Generate a PDF version of the order or quote for printing."""
    order = get_object_or_404(Order, id=order_id)

    door_items = DoorLineItem.objects.filter(order=order).select_related(
        'wood_stock', 'edge_profile', 'panel_rise', 'style'
    )
    drawer_items = order.drawer_items.all().select_related(
        'wood_stock', 'bottom'
    )
    generic_items = order.generic_items.all()

    template = 'pdf/quote_pdf.html' if order.is_quote else 'pdf/order_pdf.html'
    ctx_key = 'quote' if order.is_quote else 'order'

    context = {
        ctx_key: order,
        'order': order,
        'door_items': door_items,
        'drawer_items': drawer_items,
        'generic_items': generic_items,
    }

    html_string = render_to_string(template, context)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html_string.encode("UTF-8")), result)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{order.order_number}.pdf"'
        return response
    else:
        return HttpResponse('Error generating PDF', status=500)


def print_modal(request, order_id):
    """Return the print document selection modal."""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order/partials/print_modal.html', {'order': order})


DOCUMENT_TYPES = [
    'door_panel', 'door_cutting', 'door_gluing',
    'drawer_stock', 'drawer_cutting', 'drawer_panel',
    'lumber_sheet',
]


def print_documents(request, order_id):
    """Generate a combined PDF of the selected documents."""
    order = get_object_or_404(Order, id=order_id)

    selected = []
    for doc in DOCUMENT_TYPES:
        if request.POST.get(f'doc_{doc}'):
            qty = int(request.POST.get(f'qty_{doc}', 1))
            selected.append((doc, max(1, qty)))

    if not selected:
        return HttpResponse('No documents selected.', status=400)

    # Stub: return placeholder PDF page per selected document
    html_parts = []
    for doc, qty in selected:
        label = doc.replace('_', ' ').title()
        for _ in range(qty):
            html_parts.append(
                f'<div style="page-break-after: always; padding: 2cm; font-family: sans-serif;">'
                f'<h1>{label}</h1>'
                f'<p>Order: {order.order_number}</p>'
                f'<p style="color: #888;">(Template not yet designed)</p>'
                f'</div>'
            )

    html_string = f'<html><body>{"".join(html_parts)}</body></html>'
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html_string.encode("UTF-8")), result)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{order.order_number}_documents.pdf"'
        return response
    else:
        return HttpResponse('Error generating PDF', status=500)
