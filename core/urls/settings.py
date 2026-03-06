from django.urls import path
from ..views.settings import (
    door_settings, drawer_settings,
    edit_door_style, get_door_style, update_door_style,
    show_door_style_add, add_door_style, delete_door_style, confirm_delete_door_style,
    edit_wood_stock, get_wood_stock, update_wood_stock,
    show_wood_stock_add, add_wood_stock, delete_wood_stock, confirm_delete_wood_stock,
    edit_door_design, get_door_design, update_door_design,
    show_door_design_add, add_door_design, delete_door_design, confirm_delete_door_design,
    edit_edge_profile, get_edge_profile, update_edge_profile,
    show_edge_profile_add, add_edge_profile, delete_edge_profile, confirm_delete_edge_profile,
    edit_panel_rise, get_panel_rise, update_panel_rise,
    show_panel_rise_add, add_panel_rise, delete_panel_rise, confirm_delete_panel_rise,
    edit_panel_type, get_panel_type, update_panel_type,
    show_panel_type_add, add_panel_type, delete_panel_type, confirm_delete_panel_type,
    edit_rail_defaults, get_rail_defaults, update_rail_defaults,
    edit_drawer_woodstock, get_drawer_woodstock, update_drawer_woodstock,
    edit_drawer_bottom, get_drawer_bottom, update_drawer_bottom,
    edit_drawer_pricing, get_drawer_pricing, update_drawer_pricing,
    show_drawer_woodstock_add, add_drawer_woodstock, delete_drawer_woodstock, confirm_delete_drawer_woodstock,
    show_drawer_bottom_add, add_drawer_bottom, delete_drawer_bottom, confirm_delete_drawer_bottom,
    show_drawer_pricing_add, add_drawer_pricing, delete_drawer_pricing, confirm_delete_drawer_pricing,
    edit_drawer_defaults, get_drawer_defaults, update_drawer_defaults,
    edit_misc_settings, get_misc_settings, update_misc_settings
)

urlpatterns = [
    path('doors/', door_settings, name='door_settings'),
    path('drawers/', drawer_settings, name='drawer_settings'),

    # Door Style
    path('doors/styles/<int:style_id>/edit/', edit_door_style, name='edit_door_style'),
    path('doors/styles/<int:style_id>/', get_door_style, name='get_door_style'),
    path('doors/styles/<int:style_id>/update/', update_door_style, name='update_door_style'),
    path('doors/styles/<int:style_id>/delete/', delete_door_style, name='delete_door_style'),
    path('doors/styles/<int:style_id>/confirm-delete/', confirm_delete_door_style, name='confirm_delete_door_style'),
    path('doors/styles/add/show/', show_door_style_add, name='show_door_style_add'),
    path('doors/styles/add/', add_door_style, name='add_door_style'),

    # Wood Stock
    path('doors/wood-stock/<int:stock_id>/edit/', edit_wood_stock, name='edit_wood_stock'),
    path('doors/wood-stock/<int:stock_id>/', get_wood_stock, name='get_wood_stock'),
    path('doors/wood-stock/<int:stock_id>/update/', update_wood_stock, name='update_wood_stock'),
    path('doors/wood-stock/<int:stock_id>/delete/', delete_wood_stock, name='delete_wood_stock'),
    path('doors/wood-stock/<int:stock_id>/confirm-delete/', confirm_delete_wood_stock, name='confirm_delete_wood_stock'),
    path('doors/wood-stock/add/show/', show_wood_stock_add, name='show_wood_stock_add'),
    path('doors/wood-stock/add/', add_wood_stock, name='add_wood_stock'),

    # Drawer Wood Stock
    path('drawers/wood-stock/<int:stock_id>/edit/', edit_drawer_woodstock, name='edit_drawer_woodstock'),
    path('drawers/wood-stock/<int:stock_id>/', get_drawer_woodstock, name='get_drawer_woodstock'),
    path('drawers/wood-stock/<int:stock_id>/update/', update_drawer_woodstock, name='update_drawer_woodstock'),
    path('drawers/wood-stock/<int:stock_id>/delete/', delete_drawer_woodstock, name='delete_drawer_woodstock'),
    path('drawers/wood-stock/<int:stock_id>/confirm-delete/', confirm_delete_drawer_woodstock, name='confirm_delete_drawer_woodstock'),
    path('drawers/wood-stock/add/show/', show_drawer_woodstock_add, name='show_drawer_woodstock_add'),
    path('drawers/wood-stock/add/', add_drawer_woodstock, name='add_drawer_woodstock'),

    # Drawer Bottom Size
    path('drawers/bottom-sizes/<int:bottom_id>/edit/', edit_drawer_bottom, name='edit_drawer_bottom'),
    path('drawers/bottom-sizes/<int:bottom_id>/', get_drawer_bottom, name='get_drawer_bottom'),
    path('drawers/bottom-sizes/<int:bottom_id>/update/', update_drawer_bottom, name='update_drawer_bottom'),
    path('drawers/bottom-sizes/<int:bottom_id>/delete/', delete_drawer_bottom, name='delete_drawer_bottom'),
    path('drawers/bottom-sizes/<int:bottom_id>/confirm-delete/', confirm_delete_drawer_bottom, name='confirm_delete_drawer_bottom'),
    path('drawers/bottom-sizes/add/show/', show_drawer_bottom_add, name='show_drawer_bottom_add'),
    path('drawers/bottom-sizes/add/', add_drawer_bottom, name='add_drawer_bottom'),

    # Drawer Pricing
    path('drawers/pricing/<int:pricing_id>/edit/', edit_drawer_pricing, name='edit_drawer_pricing'),
    path('drawers/pricing/<int:pricing_id>/', get_drawer_pricing, name='get_drawer_pricing'),
    path('drawers/pricing/<int:pricing_id>/update/', update_drawer_pricing, name='update_drawer_pricing'),
    path('drawers/pricing/<int:pricing_id>/delete/', delete_drawer_pricing, name='delete_drawer_pricing'),
    path('drawers/pricing/<int:pricing_id>/confirm-delete/', confirm_delete_drawer_pricing, name='confirm_delete_drawer_pricing'),
    path('drawers/pricing/add/show/', show_drawer_pricing_add, name='show_drawer_pricing_add'),
    path('drawers/pricing/add/', add_drawer_pricing, name='add_drawer_pricing'),

    # Door Design
    path('doors/designs/<int:design_id>/edit/', edit_door_design, name='edit_door_design'),
    path('doors/designs/<int:design_id>/', get_door_design, name='get_door_design'),
    path('doors/designs/<int:design_id>/update/', update_door_design, name='update_door_design'),
    path('doors/designs/<int:design_id>/delete/', delete_door_design, name='delete_door_design'),
    path('doors/designs/<int:design_id>/confirm-delete/', confirm_delete_door_design, name='confirm_delete_door_design'),
    path('doors/designs/add/show/', show_door_design_add, name='show_door_design_add'),
    path('doors/designs/add/', add_door_design, name='add_door_design'),

    # Edge Profile
    path('doors/edge-profiles/<int:profile_id>/edit/', edit_edge_profile, name='edit_edge_profile'),
    path('doors/edge-profiles/<int:profile_id>/', get_edge_profile, name='get_edge_profile'),
    path('doors/edge-profiles/<int:profile_id>/update/', update_edge_profile, name='update_edge_profile'),
    path('doors/edge-profiles/<int:profile_id>/delete/', delete_edge_profile, name='delete_edge_profile'),
    path('doors/edge-profiles/<int:profile_id>/confirm-delete/', confirm_delete_edge_profile, name='confirm_delete_edge_profile'),
    path('doors/edge-profiles/add/show/', show_edge_profile_add, name='show_edge_profile_add'),
    path('doors/edge-profiles/add/', add_edge_profile, name='add_edge_profile'),

    # Panel Rise
    path('doors/panel-rises/<int:rise_id>/edit/', edit_panel_rise, name='edit_panel_rise'),
    path('doors/panel-rises/<int:rise_id>/', get_panel_rise, name='get_panel_rise'),
    path('doors/panel-rises/<int:rise_id>/update/', update_panel_rise, name='update_panel_rise'),
    path('doors/panel-rises/<int:rise_id>/delete/', delete_panel_rise, name='delete_panel_rise'),
    path('doors/panel-rises/<int:rise_id>/confirm-delete/', confirm_delete_panel_rise, name='confirm_delete_panel_rise'),
    path('doors/panel-rises/add/show/', show_panel_rise_add, name='show_panel_rise_add'),
    path('doors/panel-rises/add/', add_panel_rise, name='add_panel_rise'),

    # Panel Type
    path('doors/panel-types/<int:type_id>/edit/', edit_panel_type, name='edit_panel_type'),
    path('doors/panel-types/<int:type_id>/', get_panel_type, name='get_panel_type'),
    path('doors/panel-types/<int:type_id>/update/', update_panel_type, name='update_panel_type'),
    path('doors/panel-types/<int:type_id>/delete/', delete_panel_type, name='delete_panel_type'),
    path('doors/panel-types/<int:type_id>/confirm-delete/', confirm_delete_panel_type, name='confirm_delete_panel_type'),
    path('doors/panel-types/add/show/', show_panel_type_add, name='show_panel_type_add'),
    path('doors/panel-types/add/', add_panel_type, name='add_panel_type'),

    # Rail Defaults
    path('doors/rail-defaults/edit/', edit_rail_defaults, name='edit_rail_defaults'),
    path('doors/rail-defaults/', get_rail_defaults, name='get_rail_defaults'),
    path('doors/rail-defaults/update/', update_rail_defaults, name='update_rail_defaults'),

    # Drawer Default Settings
    path('drawers/defaults/edit/', edit_drawer_defaults, name='edit_drawer_defaults'),
    path('drawers/defaults/', get_drawer_defaults, name='get_drawer_defaults'),
    path('drawers/defaults/update/', update_drawer_defaults, name='update_drawer_defaults'),

    # Miscellaneous Door Settings
    path('doors/misc-settings/edit/', edit_misc_settings, name='edit_misc_settings'),
    path('doors/misc-settings/', get_misc_settings, name='get_misc_settings'),
    path('doors/misc-settings/update/', update_misc_settings, name='update_misc_settings'),
]
