from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from ..models import Style, PanelType, Design, WoodStock, EdgeProfile, PanelRise, RailDefaults, MiscellaneousDoorSettings
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseBadRequest
from django.urls import reverse


def _modal_success(request, html, target_id, swap='innerHTML'):
    response = HttpResponse(html)
    response['HX-Retarget'] = target_id
    response['HX-Reswap'] = swap
    response['HX-Trigger-After-Swap'] = 'closeModal'
    return response


def _render_tbody(request, items, display_tpl, ctx_name, add_btn_tpl):
    html = ""
    for item in items:
        html += render_to_string(display_tpl, {ctx_name: item}, request)
    html += render_to_string(add_btn_tpl, {}, request)
    return html


def _confirm_delete(request, title, message, delete_url):
    return render(request, 'partials/confirm_delete_modal.html', {
        'delete_title': title,
        'delete_message': message,
        'delete_url': delete_url,
    })


# ── Main page views ──────────────────────────────────────────────────

def door_settings(request):
    styles = Style.objects.all().select_related('panel_type', 'design')
    wood_stocks = WoodStock.objects.all()
    designs = Design.objects.all()
    edge_profiles = EdgeProfile.objects.all()
    panel_rises = PanelRise.objects.all()
    panel_types = PanelType.objects.all()
    rail_defaults = RailDefaults.objects.first()
    misc_settings = MiscellaneousDoorSettings.objects.first()

    context = {
        'styles': styles,
        'wood_stocks': wood_stocks,
        'designs': designs,
        'edge_profiles': edge_profiles,
        'panel_rises': panel_rises,
        'panel_types': panel_types,
        'rail_defaults': rail_defaults,
        'misc_settings': misc_settings,
        'title': 'Door Settings'
    }

    if request.headers.get('HX-Request'):
        return render(request, 'settings/door_content.html', context)
    return render(request, 'settings/door_settings.html', context)


def drawer_settings(request):
    from ..models.drawer import DrawerWoodStock, DrawerBottomSize, DrawerPricing, DefaultDrawerSettings

    wood_stocks = DrawerWoodStock.objects.all()
    bottom_sizes = DrawerBottomSize.objects.all()
    pricing = DrawerPricing.objects.all()
    drawer_defaults = DefaultDrawerSettings.objects.first()

    context = {
        'wood_stocks': wood_stocks,
        'bottom_sizes': bottom_sizes,
        'pricing': pricing,
        'drawer_defaults': drawer_defaults,
        'title': 'Drawer Settings'
    }

    if request.headers.get('HX-Request'):
        return render(request, 'settings/drawer_content.html', context)
    return render(request, 'settings/drawer_settings.html', context)


# ── Wood Stock CRUD ───────────────────────────────────────────────────

def edit_wood_stock(request, stock_id):
    wood = get_object_or_404(WoodStock, id=stock_id)
    return render(request, 'settings/partials/wood_stock_row_edit.html', {'wood': wood})


def get_wood_stock(request, stock_id):
    wood = get_object_or_404(WoodStock, id=stock_id)
    return render(request, 'settings/partials/wood_stock_row_display.html', {'wood': wood})


def update_wood_stock(request, stock_id):
    wood = get_object_or_404(WoodStock, id=stock_id)

    if request.method == 'POST':
        wood.name = request.POST.get('name')
        try:
            wood.raised_panel_price = Decimal(request.POST.get('raised_panel_price', '0'))
            wood.flat_panel_price = Decimal(request.POST.get('flat_panel_price', '0'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/wood_stock_row_edit.html', {
                'wood': wood,
                'errors': {'raised_panel_price': ['Please enter valid numbers for price fields']}
            }, status=422)

        try:
            wood.full_clean()
            wood.save()
        except ValidationError as e:
            return render(request, 'settings/partials/wood_stock_row_edit.html', {
                'wood': wood, 'errors': e.message_dict
            }, status=422)

        response = render(request, 'settings/partials/wood_stock_row_display.html', {'wood': wood})
        response['HX-Retarget'] = f'#wood-stock-row-{wood.id}'
        response['HX-Reswap'] = 'outerHTML'
        response['HX-Trigger-After-Swap'] = 'closeModal'
        return response

    return redirect('door_settings')


def show_wood_stock_add(request):
    return render(request, 'settings/partials/wood_stock_row_add.html')


def add_wood_stock(request):
    if request.method == 'POST':
        wood = WoodStock()
        wood.name = request.POST.get('name')
        try:
            wood.raised_panel_price = Decimal(request.POST.get('raised_panel_price', '0'))
            wood.flat_panel_price = Decimal(request.POST.get('flat_panel_price', '0'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/wood_stock_row_add.html', {
                'errors': {'raised_panel_price': ['Please enter valid numbers for price fields']}
            }, status=422)

        try:
            wood.full_clean()
            wood.save()
        except ValidationError as e:
            return render(request, 'settings/partials/wood_stock_row_add.html', {
                'errors': e.message_dict
            }, status=422)

        html = _render_tbody(request, WoodStock.objects.all(),
                             'settings/partials/wood_stock_row_display.html', 'wood',
                             'settings/partials/wood_stock_add_button.html')
        return _modal_success(request, html, '#wood-stocks-tbody')

    return redirect('door_settings')


def confirm_delete_wood_stock(request, stock_id):
    wood = get_object_or_404(WoodStock, id=stock_id)
    return _confirm_delete(request, 'Delete Wood Stock',
                           f'Are you sure you want to delete "{wood.name}"? This action cannot be undone.',
                           reverse('delete_wood_stock', args=[stock_id]))


def delete_wood_stock(request, stock_id):
    wood = get_object_or_404(WoodStock, id=stock_id)

    if request.method == 'DELETE':
        wood.delete()
        html = _render_tbody(request, WoodStock.objects.all(),
                             'settings/partials/wood_stock_row_display.html', 'wood',
                             'settings/partials/wood_stock_add_button.html')
        return _modal_success(request, html, '#wood-stocks-tbody')

    return redirect('door_settings')


# ── Door Style CRUD ───────────────────────────────────────────────────

def edit_door_style(request, style_id):
    style = get_object_or_404(Style, id=style_id)
    return render(request, 'settings/partials/style_row_edit.html', {
        'style': style,
        'panel_types': PanelType.objects.all(),
        'designs': Design.objects.all(),
    })


def get_door_style(request, style_id):
    style = get_object_or_404(Style, id=style_id)
    return render(request, 'settings/partials/style_row_display.html', {'style': style})


def update_door_style(request, style_id):
    style = get_object_or_404(Style, id=style_id)

    if request.method == 'POST':
        style.name = request.POST.get('name')
        style.panel_type_id = request.POST.get('panel_type')
        style.design_id = request.POST.get('design')

        try:
            style.price = Decimal(request.POST.get('price', '0'))
            style.panels_across = int(request.POST.get('panels_across', '1'))
            style.panels_down = int(request.POST.get('panels_down', '1'))
            style.panel_overlap = Decimal(request.POST.get('panel_overlap', '0'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/style_row_edit.html', {
                'style': style,
                'panel_types': PanelType.objects.all(),
                'designs': Design.objects.all(),
                'errors': {'price': ['Please enter valid numbers for all numeric fields']}
            }, status=422)

        style.designs_on_top = 'designs_on_top' in request.POST
        style.designs_on_bottom = 'designs_on_bottom' in request.POST

        try:
            style.full_clean()
            style.save()
        except ValidationError as e:
            return render(request, 'settings/partials/style_row_edit.html', {
                'style': style,
                'panel_types': PanelType.objects.all(),
                'designs': Design.objects.all(),
                'errors': e.message_dict
            }, status=422)

        response = render(request, 'settings/partials/style_row_display.html', {'style': style})
        response['HX-Retarget'] = f'#style-row-{style.id}'
        response['HX-Reswap'] = 'outerHTML'
        response['HX-Trigger-After-Swap'] = 'closeModal'
        return response

    return redirect('door_settings')


def show_door_style_add(request):
    return render(request, 'settings/partials/style_row_add.html', {
        'panel_types': PanelType.objects.all(),
        'designs': Design.objects.all(),
    })


def add_door_style(request):
    if request.method == 'POST':
        style = Style()
        style.name = request.POST.get('name')

        try:
            style.panel_type_id = int(request.POST.get('panel_type'))
            style.design_id = int(request.POST.get('design'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/style_row_add.html', {
                'panel_types': PanelType.objects.all(),
                'designs': Design.objects.all(),
                'errors': {'panel_type': ['Please select valid panel type and design']}
            }, status=422)

        try:
            style.price = Decimal(request.POST.get('price', '0'))
            style.panels_across = int(request.POST.get('panels_across', '1'))
            style.panels_down = int(request.POST.get('panels_down', '1'))
            style.panel_overlap = Decimal(request.POST.get('panel_overlap', '0'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/style_row_add.html', {
                'panel_types': PanelType.objects.all(),
                'designs': Design.objects.all(),
                'errors': {'price': ['Please enter valid numbers for all numeric fields']}
            }, status=422)

        style.designs_on_top = 'designs_on_top' in request.POST
        style.designs_on_bottom = 'designs_on_bottom' in request.POST

        try:
            style.full_clean()
            style.save()
        except ValidationError as e:
            return render(request, 'settings/partials/style_row_add.html', {
                'panel_types': PanelType.objects.all(),
                'designs': Design.objects.all(),
                'errors': e.message_dict
            }, status=422)

        html = _render_tbody(request,
                             Style.objects.all().select_related('panel_type', 'design'),
                             'settings/partials/style_row_display.html', 'style',
                             'settings/partials/style_add_button.html')
        return _modal_success(request, html, '#door-styles-tbody')

    return redirect('door_settings')


def confirm_delete_door_style(request, style_id):
    style = get_object_or_404(Style, id=style_id)
    return _confirm_delete(request, 'Delete Door Style',
                           f'Are you sure you want to delete "{style.name}"? This action cannot be undone.',
                           reverse('delete_door_style', args=[style_id]))


def delete_door_style(request, style_id):
    style = get_object_or_404(Style, id=style_id)

    if request.method == 'DELETE':
        style.delete()
        html = _render_tbody(request,
                             Style.objects.all().select_related('panel_type', 'design'),
                             'settings/partials/style_row_display.html', 'style',
                             'settings/partials/style_add_button.html')
        return _modal_success(request, html, '#door-styles-tbody')

    return redirect('door_settings')


# ── Door Design CRUD ──────────────────────────────────────────────────

def edit_door_design(request, design_id):
    design = get_object_or_404(Design, id=design_id)
    return render(request, 'settings/partials/design_row_edit.html', {'design': design})


def get_door_design(request, design_id):
    design = get_object_or_404(Design, id=design_id)
    return render(request, 'settings/partials/design_row_display.html', {'design': design})


def update_door_design(request, design_id):
    design = get_object_or_404(Design, id=design_id)

    if request.method == 'POST':
        design.name = request.POST.get('name')
        design.arch = 'arch' in request.POST

        try:
            design.full_clean()
            design.save()
        except ValidationError as e:
            return render(request, 'settings/partials/design_row_edit.html', {
                'design': design, 'errors': e.message_dict
            }, status=422)

        response = render(request, 'settings/partials/design_row_display.html', {'design': design})
        response['HX-Retarget'] = f'#design-row-{design.id}'
        response['HX-Reswap'] = 'outerHTML'
        response['HX-Trigger-After-Swap'] = 'closeModal'
        return response

    return redirect('door_settings')


def show_door_design_add(request):
    return render(request, 'settings/partials/door_design_row_add.html')


def add_door_design(request):
    if request.method == 'POST':
        design = Design(name=request.POST.get('name'), arch='arch' in request.POST)

        try:
            design.full_clean()
            design.save()
        except ValidationError as e:
            return render(request, 'settings/partials/door_design_row_add.html', {
                'errors': e.message_dict
            }, status=422)

        html = _render_tbody(request, Design.objects.all().order_by('name'),
                             'settings/partials/design_row_display.html', 'design',
                             'settings/partials/door_design_add_button.html')
        return _modal_success(request, html, '#door-designs-tbody')

    return redirect('door_settings')


def confirm_delete_door_design(request, design_id):
    design = get_object_or_404(Design, id=design_id)
    return _confirm_delete(request, 'Delete Door Design',
                           f'Are you sure you want to delete "{design.name}"? This action cannot be undone.',
                           reverse('delete_door_design', args=[design_id]))


def delete_door_design(request, design_id):
    design = get_object_or_404(Design, id=design_id)

    if request.method == 'DELETE':
        design.delete()
        html = _render_tbody(request, Design.objects.all().order_by('name'),
                             'settings/partials/design_row_display.html', 'design',
                             'settings/partials/door_design_add_button.html')
        return _modal_success(request, html, '#door-designs-tbody')

    return redirect('door_settings')


# ── Edge Profile CRUD ─────────────────────────────────────────────────

def edit_edge_profile(request, profile_id):
    profile = get_object_or_404(EdgeProfile, id=profile_id)
    return render(request, 'settings/partials/edge_profile_row_edit.html', {'profile': profile})


def get_edge_profile(request, profile_id):
    profile = get_object_or_404(EdgeProfile, id=profile_id)
    return render(request, 'settings/partials/edge_profile_row_display.html', {'profile': profile})


def update_edge_profile(request, profile_id):
    profile = get_object_or_404(EdgeProfile, id=profile_id)

    if request.method == 'POST':
        profile.name = request.POST.get('name')

        try:
            profile.full_clean()
            profile.save()
        except ValidationError as e:
            return render(request, 'settings/partials/edge_profile_row_edit.html', {
                'profile': profile, 'errors': e.message_dict
            }, status=422)

        response = render(request, 'settings/partials/edge_profile_row_display.html', {'profile': profile})
        response['HX-Retarget'] = f'#edge-profile-row-{profile.id}'
        response['HX-Reswap'] = 'outerHTML'
        response['HX-Trigger-After-Swap'] = 'closeModal'
        return response

    return redirect('door_settings')


def show_edge_profile_add(request):
    return render(request, 'settings/partials/edge_profile_row_add.html')


def add_edge_profile(request):
    if request.method == 'POST':
        profile = EdgeProfile(name=request.POST.get('name'))

        try:
            profile.full_clean()
            profile.save()
        except ValidationError as e:
            return render(request, 'settings/partials/edge_profile_row_add.html', {
                'errors': e.message_dict
            }, status=422)

        html = _render_tbody(request, EdgeProfile.objects.all().order_by('name'),
                             'settings/partials/edge_profile_row_display.html', 'profile',
                             'settings/partials/edge_profile_add_button.html')
        return _modal_success(request, html, '#edge-profiles-tbody')

    return redirect('door_settings')


def confirm_delete_edge_profile(request, profile_id):
    profile = get_object_or_404(EdgeProfile, id=profile_id)
    return _confirm_delete(request, 'Delete Edge Profile',
                           f'Are you sure you want to delete "{profile.name}"? This action cannot be undone.',
                           reverse('delete_edge_profile', args=[profile_id]))


def delete_edge_profile(request, profile_id):
    profile = get_object_or_404(EdgeProfile, id=profile_id)

    if request.method == 'DELETE':
        profile.delete()
        html = _render_tbody(request, EdgeProfile.objects.all().order_by('name'),
                             'settings/partials/edge_profile_row_display.html', 'profile',
                             'settings/partials/edge_profile_add_button.html')
        return _modal_success(request, html, '#edge-profiles-tbody')

    return redirect('door_settings')


# ── Panel Rise CRUD ───────────────────────────────────────────────────

def edit_panel_rise(request, rise_id):
    rise = get_object_or_404(PanelRise, id=rise_id)
    return render(request, 'settings/partials/panel_rise_row_edit.html', {'rise': rise})


def get_panel_rise(request, rise_id):
    rise = get_object_or_404(PanelRise, id=rise_id)
    return render(request, 'settings/partials/panel_rise_row_display.html', {'rise': rise})


def update_panel_rise(request, rise_id):
    rise = get_object_or_404(PanelRise, id=rise_id)

    if request.method == 'POST':
        rise.name = request.POST.get('name')

        try:
            rise.full_clean()
            rise.save()
        except ValidationError as e:
            return render(request, 'settings/partials/panel_rise_row_edit.html', {
                'rise': rise, 'errors': e.message_dict
            }, status=422)

        response = render(request, 'settings/partials/panel_rise_row_display.html', {'rise': rise})
        response['HX-Retarget'] = f'#panel-rise-row-{rise.id}'
        response['HX-Reswap'] = 'outerHTML'
        response['HX-Trigger-After-Swap'] = 'closeModal'
        return response

    return redirect('door_settings')


def show_panel_rise_add(request):
    return render(request, 'settings/partials/panel_rise_row_add.html')


def add_panel_rise(request):
    if request.method == 'POST':
        rise = PanelRise(name=request.POST.get('name'))

        try:
            rise.full_clean()
            rise.save()
        except ValidationError as e:
            return render(request, 'settings/partials/panel_rise_row_add.html', {
                'errors': e.message_dict
            }, status=422)

        html = _render_tbody(request, PanelRise.objects.all().order_by('name'),
                             'settings/partials/panel_rise_row_display.html', 'rise',
                             'settings/partials/panel_rise_add_button.html')
        return _modal_success(request, html, '#panel-rises-tbody')

    return redirect('door_settings')


def confirm_delete_panel_rise(request, rise_id):
    rise = get_object_or_404(PanelRise, id=rise_id)
    return _confirm_delete(request, 'Delete Panel Raise',
                           f'Are you sure you want to delete "{rise.name}"? This action cannot be undone.',
                           reverse('delete_panel_rise', args=[rise_id]))


def delete_panel_rise(request, rise_id):
    rise = get_object_or_404(PanelRise, id=rise_id)

    if request.method == 'DELETE':
        rise.delete()
        html = _render_tbody(request, PanelRise.objects.all().order_by('name'),
                             'settings/partials/panel_rise_row_display.html', 'rise',
                             'settings/partials/panel_rise_add_button.html')
        return _modal_success(request, html, '#panel-rises-tbody')

    return redirect('door_settings')


# ── Panel Type CRUD ───────────────────────────────────────────────────

def edit_panel_type(request, type_id):
    panel_type = get_object_or_404(PanelType, id=type_id)
    return render(request, 'settings/partials/panel_type_row_edit.html', {'type': panel_type})


def get_panel_type(request, type_id):
    panel_type = get_object_or_404(PanelType, id=type_id)
    return render(request, 'settings/partials/panel_type_row_display.html', {'type': panel_type})


def update_panel_type(request, type_id):
    panel_type = get_object_or_404(PanelType, id=type_id)

    if request.method == 'POST':
        panel_type.name = request.POST.get('name')

        try:
            panel_type.minimum_sq_ft = Decimal(request.POST.get('minimum_sq_ft', '0'))
            panel_type.surcharge_width = Decimal(request.POST.get('surcharge_width', '0'))
            panel_type.surcharge_height = Decimal(request.POST.get('surcharge_height', '0'))
            panel_type.surcharge_percent = Decimal(request.POST.get('surcharge_percent', '0'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/panel_type_row_edit.html', {
                'type': panel_type,
                'errors': {'surcharge_width': ['Please enter valid numbers for all numeric fields']}
            }, status=422)

        panel_type.use_flat_panel_price = 'use_flat_panel_price' in request.POST

        try:
            panel_type.full_clean()
            panel_type.save()
        except ValidationError as e:
            return render(request, 'settings/partials/panel_type_row_edit.html', {
                'type': panel_type, 'errors': e.message_dict
            }, status=422)

        response = render(request, 'settings/partials/panel_type_row_display.html', {'type': panel_type})
        response['HX-Retarget'] = f'#panel-type-row-{panel_type.id}'
        response['HX-Reswap'] = 'outerHTML'
        response['HX-Trigger-After-Swap'] = 'closeModal'
        return response

    return redirect('door_settings')


def show_panel_type_add(request):
    return render(request, 'settings/partials/panel_type_row_add.html')


def add_panel_type(request):
    if request.method == 'POST':
        panel_type = PanelType()
        panel_type.name = request.POST.get('name')

        try:
            panel_type.minimum_sq_ft = Decimal(request.POST.get('minimum_sq_ft', '0'))
            panel_type.surcharge_width = Decimal(request.POST.get('surcharge_width', '0'))
            panel_type.surcharge_height = Decimal(request.POST.get('surcharge_height', '0'))
            panel_type.surcharge_percent = Decimal(request.POST.get('surcharge_percent', '0'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/panel_type_row_add.html', {
                'errors': {'surcharge_width': ['Please enter valid numbers for all numeric fields']}
            }, status=422)

        panel_type.use_flat_panel_price = 'use_flat_panel_price' in request.POST

        try:
            panel_type.full_clean()
            panel_type.save()
        except ValidationError as e:
            return render(request, 'settings/partials/panel_type_row_add.html', {
                'errors': e.message_dict
            }, status=422)

        html = _render_tbody(request, PanelType.objects.all().order_by('name'),
                             'settings/partials/panel_type_row_display.html', 'type',
                             'settings/partials/panel_type_add_button.html')
        return _modal_success(request, html, '#panel-types-tbody')

    return redirect('door_settings')


def confirm_delete_panel_type(request, type_id):
    panel_type = get_object_or_404(PanelType, id=type_id)
    return _confirm_delete(request, 'Delete Panel Type',
                           f'Are you sure you want to delete "{panel_type.name}"? This action cannot be undone.',
                           reverse('delete_panel_type', args=[type_id]))


def delete_panel_type(request, type_id):
    panel_type = get_object_or_404(PanelType, id=type_id)

    if request.method == 'DELETE':
        panel_type.delete()
        html = _render_tbody(request, PanelType.objects.all().order_by('name'),
                             'settings/partials/panel_type_row_display.html', 'type',
                             'settings/partials/panel_type_add_button.html')
        return _modal_success(request, html, '#panel-types-tbody')

    return redirect('door_settings')


# ── Drawer Wood Stock CRUD ────────────────────────────────────────────

def edit_drawer_woodstock(request, stock_id):
    from ..models.drawer import DrawerWoodStock
    wood = get_object_or_404(DrawerWoodStock, id=stock_id)
    return render(request, 'settings/partials/drawer_woodstock_row_edit.html', {'wood': wood})


def get_drawer_woodstock(request, stock_id):
    from ..models.drawer import DrawerWoodStock
    wood = get_object_or_404(DrawerWoodStock, id=stock_id)
    return render(request, 'settings/partials/drawer_woodstock_row_display.html', {'wood': wood})


def update_drawer_woodstock(request, stock_id):
    from ..models.drawer import DrawerWoodStock
    wood = get_object_or_404(DrawerWoodStock, id=stock_id)

    if request.method == 'POST':
        wood.name = request.POST.get('name')
        try:
            wood.price = Decimal(request.POST.get('price', '0'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/drawer_woodstock_row_edit.html', {
                'wood': wood,
                'errors': {'price': ['Please enter a valid number for price']}
            }, status=422)

        try:
            wood.full_clean()
            wood.save()
        except ValidationError as e:
            return render(request, 'settings/partials/drawer_woodstock_row_edit.html', {
                'wood': wood, 'errors': e.message_dict
            }, status=422)

        response = render(request, 'settings/partials/drawer_woodstock_row_display.html', {'wood': wood})
        response['HX-Retarget'] = f'#drawer-wood-stock-row-{wood.id}'
        response['HX-Reswap'] = 'outerHTML'
        response['HX-Trigger-After-Swap'] = 'closeModal'
        return response

    return redirect('drawer_settings')


def show_drawer_woodstock_add(request):
    return render(request, 'settings/partials/drawer_woodstock_row_add.html')


def add_drawer_woodstock(request):
    from ..models.drawer import DrawerWoodStock

    if request.method == 'POST':
        wood = DrawerWoodStock()
        wood.name = request.POST.get('name')
        try:
            wood.price = Decimal(request.POST.get('price', '0'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/drawer_woodstock_row_add.html', {
                'errors': {'price': ['Please enter a valid number for price']}
            }, status=422)

        try:
            wood.full_clean()
            wood.save()
        except ValidationError as e:
            return render(request, 'settings/partials/drawer_woodstock_row_add.html', {
                'errors': e.message_dict
            }, status=422)

        html = _render_tbody(request, DrawerWoodStock.objects.all(),
                             'settings/partials/drawer_woodstock_row_display.html', 'wood',
                             'settings/partials/drawer_woodstock_add_button.html')
        return _modal_success(request, html, '#drawer-wood-stocks-tbody')

    return redirect('drawer_settings')


def confirm_delete_drawer_woodstock(request, stock_id):
    from ..models.drawer import DrawerWoodStock
    wood = get_object_or_404(DrawerWoodStock, id=stock_id)
    return _confirm_delete(request, 'Delete Drawer Wood Stock',
                           f'Are you sure you want to delete "{wood.name}"? This action cannot be undone.',
                           reverse('delete_drawer_woodstock', args=[stock_id]))


def delete_drawer_woodstock(request, stock_id):
    from ..models.drawer import DrawerWoodStock
    wood = get_object_or_404(DrawerWoodStock, id=stock_id)

    if request.method == 'DELETE':
        wood.delete()
        html = _render_tbody(request, DrawerWoodStock.objects.all(),
                             'settings/partials/drawer_woodstock_row_display.html', 'wood',
                             'settings/partials/drawer_woodstock_add_button.html')
        return _modal_success(request, html, '#drawer-wood-stocks-tbody')

    return redirect('drawer_settings')


# ── Drawer Bottom Size CRUD ───────────────────────────────────────────

def edit_drawer_bottom(request, bottom_id):
    from ..models.drawer import DrawerBottomSize
    bottom = get_object_or_404(DrawerBottomSize, id=bottom_id)
    return render(request, 'settings/partials/drawer_bottom_row_edit.html', {'bottom': bottom})


def get_drawer_bottom(request, bottom_id):
    from ..models.drawer import DrawerBottomSize
    bottom = get_object_or_404(DrawerBottomSize, id=bottom_id)
    return render(request, 'settings/partials/drawer_bottom_row_display.html', {'bottom': bottom})


def update_drawer_bottom(request, bottom_id):
    from ..models.drawer import DrawerBottomSize
    bottom = get_object_or_404(DrawerBottomSize, id=bottom_id)

    if request.method == 'POST':
        bottom.name = request.POST.get('name')
        try:
            bottom.thickness = Decimal(request.POST.get('thickness', '0.001'))
            bottom.price = Decimal(request.POST.get('price', '0'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/drawer_bottom_row_edit.html', {
                'bottom': bottom,
                'errors': {'thickness': ['Please enter valid numbers for thickness and price']}
            }, status=422)

        try:
            bottom.full_clean()
            bottom.save()
        except ValidationError as e:
            return render(request, 'settings/partials/drawer_bottom_row_edit.html', {
                'bottom': bottom, 'errors': e.message_dict
            }, status=422)

        response = render(request, 'settings/partials/drawer_bottom_row_display.html', {'bottom': bottom})
        response['HX-Retarget'] = f'#drawer-bottom-row-{bottom.id}'
        response['HX-Reswap'] = 'outerHTML'
        response['HX-Trigger-After-Swap'] = 'closeModal'
        return response

    return redirect('drawer_settings')


def show_drawer_bottom_add(request):
    return render(request, 'settings/partials/drawer_bottom_row_add.html')


def add_drawer_bottom(request):
    from ..models.drawer import DrawerBottomSize

    if request.method == 'POST':
        bottom = DrawerBottomSize()
        bottom.name = request.POST.get('name')
        try:
            bottom.thickness = Decimal(request.POST.get('thickness', '0.001'))
            bottom.price = Decimal(request.POST.get('price', '0'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/drawer_bottom_row_add.html', {
                'errors': {'thickness': ['Please enter valid numbers for thickness and price']}
            }, status=422)

        try:
            bottom.full_clean()
            bottom.save()
        except ValidationError as e:
            return render(request, 'settings/partials/drawer_bottom_row_add.html', {
                'errors': e.message_dict
            }, status=422)

        html = _render_tbody(request, DrawerBottomSize.objects.all(),
                             'settings/partials/drawer_bottom_row_display.html', 'bottom',
                             'settings/partials/drawer_bottom_add_button.html')
        return _modal_success(request, html, '#drawer-bottom-sizes-tbody')

    return redirect('drawer_settings')


def confirm_delete_drawer_bottom(request, bottom_id):
    from ..models.drawer import DrawerBottomSize
    bottom = get_object_or_404(DrawerBottomSize, id=bottom_id)
    return _confirm_delete(request, 'Delete Bottom Size',
                           f'Are you sure you want to delete "{bottom.name}"? This action cannot be undone.',
                           reverse('delete_drawer_bottom', args=[bottom_id]))


def delete_drawer_bottom(request, bottom_id):
    from ..models.drawer import DrawerBottomSize
    bottom = get_object_or_404(DrawerBottomSize, id=bottom_id)

    if request.method == 'DELETE':
        bottom.delete()
        html = _render_tbody(request, DrawerBottomSize.objects.all(),
                             'settings/partials/drawer_bottom_row_display.html', 'bottom',
                             'settings/partials/drawer_bottom_add_button.html')
        return _modal_success(request, html, '#drawer-bottom-sizes-tbody')

    return redirect('drawer_settings')


# ── Drawer Pricing CRUD ──────────────────────────────────────────────

def edit_drawer_pricing(request, pricing_id):
    from ..models.drawer import DrawerPricing
    pricing = get_object_or_404(DrawerPricing, id=pricing_id)
    return render(request, 'settings/partials/drawer_pricing_row_edit.html', {'pricing': pricing})


def get_drawer_pricing(request, pricing_id):
    from ..models.drawer import DrawerPricing
    pricing = get_object_or_404(DrawerPricing, id=pricing_id)
    return render(request, 'settings/partials/drawer_pricing_row_display.html', {'pricing': pricing})


def update_drawer_pricing(request, pricing_id):
    from ..models.drawer import DrawerPricing
    pricing = get_object_or_404(DrawerPricing, id=pricing_id)

    if request.method == 'POST':
        try:
            pricing.price = Decimal(request.POST.get('price', '0.01'))
            pricing.height = Decimal(request.POST.get('height', '0.01'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/drawer_pricing_row_edit.html', {
                'pricing': pricing,
                'errors': {'price': ['Please enter valid numbers for price and height']}
            }, status=422)

        try:
            pricing.full_clean()
            pricing.save()
        except ValidationError as e:
            return render(request, 'settings/partials/drawer_pricing_row_edit.html', {
                'pricing': pricing, 'errors': e.message_dict
            }, status=422)

        response = render(request, 'settings/partials/drawer_pricing_row_display.html', {'pricing': pricing})
        response['HX-Retarget'] = f'#drawer-pricing-row-{pricing.id}'
        response['HX-Reswap'] = 'outerHTML'
        response['HX-Trigger-After-Swap'] = 'closeModal'
        return response

    return redirect('drawer_settings')


def show_drawer_pricing_add(request):
    return render(request, 'settings/partials/drawer_pricing_row_add.html')


def add_drawer_pricing(request):
    from ..models.drawer import DrawerPricing

    if request.method == 'POST':
        pricing = DrawerPricing()
        try:
            pricing.price = Decimal(request.POST.get('price', '0.01'))
            pricing.height = Decimal(request.POST.get('height', '0.01'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/drawer_pricing_row_add.html', {
                'errors': {'price': ['Please enter valid numbers for price and height']}
            }, status=422)

        try:
            pricing.full_clean()
            pricing.save()
        except ValidationError as e:
            return render(request, 'settings/partials/drawer_pricing_row_add.html', {
                'errors': e.message_dict
            }, status=422)

        html = _render_tbody(request, DrawerPricing.objects.all(),
                             'settings/partials/drawer_pricing_row_display.html', 'pricing',
                             'settings/partials/drawer_pricing_add_button.html')
        return _modal_success(request, html, '#drawer-pricing-tbody')

    return redirect('drawer_settings')


def confirm_delete_drawer_pricing(request, pricing_id):
    from ..models.drawer import DrawerPricing
    pricing = get_object_or_404(DrawerPricing, id=pricing_id)
    return _confirm_delete(request, 'Delete Pricing',
                           f'Are you sure you want to delete this pricing configuration (${pricing.price})? This action cannot be undone.',
                           reverse('delete_drawer_pricing', args=[pricing_id]))


def delete_drawer_pricing(request, pricing_id):
    from ..models.drawer import DrawerPricing
    pricing = get_object_or_404(DrawerPricing, id=pricing_id)

    if request.method == 'DELETE':
        pricing.delete()
        html = _render_tbody(request, DrawerPricing.objects.all(),
                             'settings/partials/drawer_pricing_row_display.html', 'pricing',
                             'settings/partials/drawer_pricing_add_button.html')
        return _modal_success(request, html, '#drawer-pricing-tbody')

    return redirect('drawer_settings')


# ── Rail Defaults (edit only) ─────────────────────────────────────────

def edit_rail_defaults(request):
    defaults = RailDefaults.objects.first()
    if not defaults:
        defaults = RailDefaults.objects.create(
            top=Decimal('2.50'), bottom=Decimal('2.50'),
            left=Decimal('2.50'), right=Decimal('2.50'),
            interior_rail_size=Decimal('2.50')
        )
    return render(request, 'settings/partials/rail_defaults_row_edit.html', {'defaults': defaults})


def get_rail_defaults(request):
    defaults = RailDefaults.objects.first()
    if not defaults:
        defaults = RailDefaults.objects.create(
            top=Decimal('2.50'), bottom=Decimal('2.50'),
            left=Decimal('2.50'), right=Decimal('2.50'),
            interior_rail_size=Decimal('2.50')
        )
    return render(request, 'settings/partials/rail_defaults_row_display.html', {'defaults': defaults})


def update_rail_defaults(request):
    defaults = RailDefaults.objects.first()
    if not defaults:
        defaults = RailDefaults.objects.create(
            top=Decimal('2.50'), bottom=Decimal('2.50'),
            left=Decimal('2.50'), right=Decimal('2.50'),
            interior_rail_size=Decimal('2.50')
        )

    if request.method == 'POST':
        try:
            defaults.top = Decimal(request.POST.get('top', '2.50'))
            defaults.bottom = Decimal(request.POST.get('bottom', '2.50'))
            defaults.left = Decimal(request.POST.get('left', '2.50'))
            defaults.right = Decimal(request.POST.get('right', '2.50'))
            defaults.interior_rail_size = Decimal(request.POST.get('interior_rail_size', '2.50'))
            defaults.full_clean()
            defaults.save()
        except (ValidationError, ValueError) as e:
            if isinstance(e, ValidationError):
                errors = e.message_dict
            else:
                errors = {'top': ['Invalid decimal value']}
            return render(request, 'settings/partials/rail_defaults_row_edit.html', {
                'defaults': defaults, 'errors': errors
            }, status=422)

        response = render(request, 'settings/partials/rail_defaults_row_display.html', {'defaults': defaults})
        response['HX-Retarget'] = '#rail-defaults-content'
        response['HX-Reswap'] = 'innerHTML'
        response['HX-Trigger-After-Swap'] = 'closeModal'
        return response

    return redirect('door_settings')


# ── Miscellaneous Door Settings (edit only) ───────────────────────────

def edit_misc_settings(request):
    settings = MiscellaneousDoorSettings.objects.first()
    panel_types = PanelType.objects.all()
    if not settings:
        settings = MiscellaneousDoorSettings.objects.create(
            extra_height=Decimal('0.125'), extra_width=Decimal('0.125'),
            glue_min_width=Decimal('8.000'), rail_extra=Decimal('0.125'),
            drawer_front=PanelType.objects.first(), drawer_slab=PanelType.objects.first()
        )
    return render(request, 'settings/partials/misc_settings_row_edit.html', {
        'settings': settings, 'panel_types': panel_types,
    })


def get_misc_settings(request):
    settings = MiscellaneousDoorSettings.objects.first()
    if not settings:
        settings = MiscellaneousDoorSettings.objects.create(
            extra_height=Decimal('0.125'), extra_width=Decimal('0.125'),
            glue_min_width=Decimal('8.000'), rail_extra=Decimal('0.125'),
            drawer_front=PanelType.objects.first(), drawer_slab=PanelType.objects.first()
        )
    return render(request, 'settings/partials/misc_settings_row_display.html', {'settings': settings})


def update_misc_settings(request):
    settings = MiscellaneousDoorSettings.objects.first()
    panel_types = PanelType.objects.all()
    if not settings:
        settings = MiscellaneousDoorSettings.objects.create(
            extra_height=Decimal('0.125'), extra_width=Decimal('0.125'),
            glue_min_width=Decimal('8.000'), rail_extra=Decimal('0.125'),
            drawer_front=PanelType.objects.first(), drawer_slab=PanelType.objects.first()
        )

    if request.method == 'POST':
        try:
            settings.extra_height = Decimal(request.POST.get('extra_height', '0.125'))
            settings.extra_width = Decimal(request.POST.get('extra_width', '0.125'))
            settings.glue_min_width = Decimal(request.POST.get('glue_min_width', '8.000'))
            settings.rail_extra = Decimal(request.POST.get('rail_extra', '0.125'))
            settings.drawer_front_id = request.POST.get('drawer_front')
            settings.drawer_slab_id = request.POST.get('drawer_slab')
            settings.full_clean()
            settings.save()
        except (ValidationError, InvalidOperation) as e:
            if isinstance(e, ValidationError):
                errors = e.message_dict
            else:
                errors = {'extra_height': ['Invalid decimal value']}
            return render(request, 'settings/partials/misc_settings_row_edit.html', {
                'settings': settings, 'panel_types': panel_types, 'errors': errors
            }, status=422)

        response = render(request, 'settings/partials/misc_settings_row_display.html', {'settings': settings})
        response['HX-Retarget'] = '#misc-settings-content'
        response['HX-Reswap'] = 'innerHTML'
        response['HX-Trigger-After-Swap'] = 'closeModal'
        return response

    return redirect('door_settings')


# ── Drawer Default Settings (edit only) ───────────────────────────────

def edit_drawer_defaults(request):
    from ..models.drawer import DefaultDrawerSettings
    defaults = DefaultDrawerSettings.objects.first()
    if not defaults:
        defaults = DefaultDrawerSettings.objects.create()
    return render(request, 'settings/partials/drawer_defaults_row_edit.html', {'defaults': defaults})


def get_drawer_defaults(request):
    from ..models.drawer import DefaultDrawerSettings
    defaults = DefaultDrawerSettings.objects.first()
    if not defaults:
        defaults = DefaultDrawerSettings.objects.create()
    return render(request, 'settings/partials/drawer_defaults_row_display.html', {'defaults': defaults})


def update_drawer_defaults(request):
    from ..models.drawer import DefaultDrawerSettings

    if request.method == 'POST':
        defaults = DefaultDrawerSettings.objects.first()
        if not defaults:
            defaults = DefaultDrawerSettings.objects.create()

        defaults.surcharge_width = request.POST.get('surcharge_width', 0.00)
        defaults.surcharge_depth = request.POST.get('surcharge_depth', 0.00)
        defaults.surcharge_percent = request.POST.get('surcharge_percent', 0.00)
        defaults.finish_charge = request.POST.get('finish_charge', 0.00)
        defaults.undermount_charge = request.POST.get('undermount_charge', 0.00)
        defaults.ends_cutting_adjustment = request.POST.get('ends_cutting_adjustment', 0.000)
        defaults.sides_cutting_adjustment = request.POST.get('sides_cutting_adjustment', 0.000)
        defaults.plywood_size_adjustment = request.POST.get('plywood_size_adjustment', 0.000)
        defaults.save()

        response = render(request, 'settings/partials/drawer_defaults_row_display.html', {'defaults': defaults})
        response['HX-Retarget'] = '#drawer-defaults-content'
        response['HX-Reswap'] = 'innerHTML'
        response['HX-Trigger-After-Swap'] = 'closeModal'
        return response

    return HttpResponseBadRequest("Invalid request method")
