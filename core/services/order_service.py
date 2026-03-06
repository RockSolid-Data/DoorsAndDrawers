"""
Service for handling order and quote operations.
"""
from decimal import Decimal
from django.db import transaction, DatabaseError, IntegrityError
from ..models import Order
from ..models.door import DoorLineItem
from ..models.drawer import DrawerLineItem
from ..models.line_item import GenericLineItem
from .door_defaults_service import DoorDefaultsService


class OrderService:
    """
    Service class that handles operations related to orders and quotes.
    Encapsulates the business logic for creating, updating, and processing orders.
    """

    def __init__(self):
        self.door_defaults_service = DoorDefaultsService()

    @staticmethod
    def create_from_session(form_data, session_data, is_quote=False):
        """
        Create an order or quote from form data and session data.
        Uses atomic transactions to ensure data integrity.
        
        Args:
            form_data (dict): The cleaned form data
            session_data (dict): The session data containing order info and line items
            is_quote (bool): Whether to create a quote or an order
            
        Returns:
            tuple: (success, order, error_message)
        """
        # Validate the session data
        is_valid, error = OrderService._validate_session_data(form_data, session_data)
        if not is_valid:
            return False, None, error
            
        try:
            # Use atomic transaction to ensure all-or-nothing database operations
            with transaction.atomic():
                # Create the order/quote base object
                order_instance = OrderService._create_order_base(form_data, is_quote)
                # Process all line items
                items_count = OrderService._process_line_items(order_instance, session_data.get('items', []))

                # Calculate and save totals
                order_instance.calculate_totals()
                order_instance.save()

                return True, order_instance, None
                
        except IntegrityError as e:
            return False, None, f"Data integrity error: {str(e)}"
        except DatabaseError as e:
            return False, None, f"Database error: {str(e)}"
        except Exception as e:
            return False, None, f"Error creating {'quote' if is_quote else 'order'}: {str(e)}"

    @staticmethod
    def _validate_session_data(form_data, session_data):
        """
        Validate session data against form data.
        
        Args:
            form_data (dict): The cleaned form data
            session_data (dict): The session data
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check if session data exists
        if not session_data:
            return False, "No session data found. Please start over."
            
        # Check if there are items in the session
        if 'items' not in session_data or not session_data['items']:
            return False, "No line items found. Please add items before creating."
            
        # Check if a customer is selected
        if 'customer' not in session_data:
            return False, "Please select a customer before finalizing."
            
        # Check if customer ID matches the form
        session_customer = session_data.get('customer')
        form_customer = form_data.get('customer').id
        
        if str(session_customer) != str(form_customer):
            return False, "Customer information mismatch. Please try again."
            
        # Add more validation as needed
        
        return True, None

    @staticmethod
    def _create_order_base(form_data, is_quote=False):
        """
        Create the base order object.
        
        Args:
            form_data (dict): Cleaned form data
            is_quote (bool): Whether this is a quote
            
        Returns:
            Order: The created order instance
        """
        # Create and save the order/quote
        order = Order(
            customer=form_data['customer'],
            is_quote=is_quote,
            billing_address1=form_data['billing_address1'],
            billing_address2=form_data.get('billing_address2', ''),
            order_date=form_data['order_date'],
            notes=form_data.get('notes', '')
        )
        order.save()
        return order

    @staticmethod
    def _process_line_items(order, line_items):
        """
        Process all line items and add them to the order.
        
        Args:
            order (Order): The order instance
            line_items (list): List of line item dictionaries from session
            
        Returns:
            int: Number of line items processed
        """
        items_count = 0
        for item in line_items:
            items_count += 1
            item_type = item.get('type')
            
            if item_type == 'door':
                OrderService._create_door_line_item(order, item)
            elif item_type == 'drawer':
                OrderService._create_drawer_line_item(order, item)
            elif item_type == 'other':
                OrderService._create_generic_line_item(order, item)

        return items_count

    @staticmethod
    def update_from_session(order, form_data, session_data):
        """
        Update an existing order/quote from form data and session data.
        Deletes all existing line items and recreates them from the session.

        Returns:
            tuple: (success, order, error_message)
        """
        is_valid, error = OrderService._validate_session_data(form_data, session_data)
        if not is_valid:
            return False, None, error

        try:
            with transaction.atomic():
                order.customer = form_data['customer']
                order.billing_address1 = form_data['billing_address1']
                order.billing_address2 = form_data.get('billing_address2', '')
                order.order_date = form_data['order_date']
                order.notes = form_data.get('notes', '')

                order.door_items.all().delete()
                order.drawer_items.all().delete()
                order.generic_items.all().delete()

                OrderService._process_line_items(order, session_data.get('items', []))
                order.calculate_totals()
                order.save()

                return True, order, None

        except IntegrityError as e:
            return False, None, f"Data integrity error: {str(e)}"
        except DatabaseError as e:
            return False, None, f"Database error: {str(e)}"
        except Exception as e:
            return False, None, f"Error updating {'quote' if order.is_quote else 'order'}: {str(e)}"

    @staticmethod
    def serialize_to_session(order):
        """
        Convert an order's DB line items into the session dictionary format
        used by line_items_table.html. Returns the full session data dict.
        """
        items = []

        for item in order.door_items.all().select_related(
            'wood_stock', 'edge_profile', 'panel_rise', 'style'
        ):
            items.append({
                'type': 'door',
                'wood_stock': {'id': item.wood_stock_id, 'name': item.wood_stock.name},
                'edge_profile': {'id': item.edge_profile_id, 'name': item.edge_profile.name},
                'panel_rise': {'id': item.panel_rise_id, 'name': item.panel_rise.name},
                'style': {'id': item.style_id, 'name': str(item.style)},
                'width': str(item.width),
                'height': str(item.height),
                'quantity': str(item.quantity),
                'price_per_unit': str(item.price_per_unit),
                'total_price': str(item.total_price),
                'rail_top': str(item.rail_top),
                'rail_bottom': str(item.rail_bottom),
                'rail_left': str(item.rail_left),
                'rail_right': str(item.rail_right),
                'interior_rail_size': str(item.interior_rail_size),
                'custom_price': item.custom_price,
            })

        for item in order.drawer_items.all().select_related('wood_stock', 'bottom'):
            items.append({
                'type': 'drawer',
                'wood_stock': {'id': item.wood_stock_id, 'name': item.wood_stock.name},
                'bottom': {'id': item.bottom_id, 'name': item.bottom.name},
                'width': str(item.width),
                'height': str(item.height),
                'depth': str(item.depth),
                'quantity': str(item.quantity),
                'undermount': item.undermount,
                'finishing': item.finishing,
                'price_per_unit': str(item.price_per_unit),
                'total_price': str(item.total_price),
                'custom_price': item.custom_price,
            })

        for item in order.generic_items.all():
            items.append({
                'type': 'other',
                'name': item.name,
                'quantity': str(item.quantity),
                'price_per_unit': str(item.price_per_unit),
                'total_price': str(item.total_price),
                'custom_price': item.custom_price,
            })

        return {
            'customer': str(order.customer_id),
            'billing_address1': order.billing_address1,
            'billing_address2': order.billing_address2 or '',
            'items': items,
        }

    @staticmethod
    def _create_door_line_item(order, item_data):
        """
        Create a door line item from session data.
        
        Args:
            order (Order): The order to attach the item to
            item_data (dict): The line item data from session
            
        Returns:
            DoorLineItem: The created door line item
        """
        # Get door components
        width = Decimal(item_data['width'])
        height = Decimal(item_data['height'])
        quantity = int(item_data['quantity'])
        custom_price = item_data.get('custom_price', False)
        
        # Only use the stored price_per_unit if custom_price is True
        price_per_unit = Decimal(item_data['price_per_unit']) if custom_price else Decimal('0.00')
        
        # Get rail values from session if available, otherwise use defaults
        door_defaults_service = DoorDefaultsService()
        
        # Get customer-specific interior rail size or global default
        interior_rail_size = door_defaults_service.get_rail_size(
            order.customer, 
            'interior_rail_size'
        ) if order.customer else door_defaults_service.global_defaults['interior_rail_size']
        
        # Get customer defaults for sanding options
        customer_defaults = door_defaults_service.get_defaults(order.customer) if order.customer else {}
        sand_edge = customer_defaults.get('sand_edge', False)
        sand_cross_grain = customer_defaults.get('sand_cross_grain', False)
        
        # Create door line item
        door_item = DoorLineItem(
            order=order,
            wood_stock_id=item_data['wood_stock']['id'],
            edge_profile_id=item_data['edge_profile']['id'],
            panel_rise_id=item_data['panel_rise']['id'],
            style_id=item_data['style']['id'],
            width=width,
            height=height,
            quantity=quantity,
            price_per_unit=price_per_unit,
            rail_top=Decimal(item_data.get('rail_top', door_defaults_service.global_defaults['rail_top'])),
            rail_bottom=Decimal(item_data.get('rail_bottom', door_defaults_service.global_defaults['rail_bottom'])),
            rail_left=Decimal(item_data.get('rail_left', door_defaults_service.global_defaults['rail_left'])),
            rail_right=Decimal(item_data.get('rail_right', door_defaults_service.global_defaults['rail_right'])),
            interior_rail_size=interior_rail_size,
            custom_price=custom_price,
            sand_edge=sand_edge,
            sand_cross_grain=sand_cross_grain
        )
        door_item.save()
        return door_item

    @staticmethod
    def _create_drawer_line_item(order, item_data):
        """
        Create a drawer line item from session data.
        
        Args:
            order (Order): The order to attach the item to
            item_data (dict): The line item data from session
            
        Returns:
            DrawerLineItem: The created drawer line item
        """
        # Get drawer components
        width = Decimal(item_data['width'])
        height = Decimal(item_data['height'])
        depth = Decimal(item_data['depth'])
        quantity = int(item_data['quantity'])
        custom_price = item_data.get('custom_price', False)
        
        # Only use the stored price_per_unit if custom_price is True
        price_per_unit = Decimal(item_data['price_per_unit']) if custom_price else Decimal('0.00')
        
        # Create drawer line item
        drawer_item = DrawerLineItem(
            order=order,
            wood_stock_id=item_data['wood_stock']['id'],
            bottom_id=item_data['bottom']['id'],
            width=width,
            height=height,
            depth=depth,
            quantity=quantity,
            price_per_unit=price_per_unit,
            undermount=item_data.get('undermount', False),
            finishing=item_data.get('finishing', False),
            custom_price=custom_price
        )
        drawer_item.save()
        return drawer_item

    @staticmethod
    def _create_generic_line_item(order, item_data):
        """
        Create a generic line item from session data.
        
        Args:
            order (Order): The order to attach the item to
            item_data (dict): The line item data from session
            
        Returns:
            GenericLineItem: The created generic line item
        """
        # Get item details
        name = item_data.get('name')
        quantity = int(item_data.get('quantity'))
        custom_price = item_data.get('custom_price', False)
        
        # Price per unit is always required for generic items
        price_per_unit = Decimal(item_data.get('price_per_unit'))
        
        # Create generic line item
        generic_item = GenericLineItem(
            order=order,
            name=name,
            quantity=quantity,
            price_per_unit=price_per_unit,
            custom_price=custom_price
        )
        generic_item.save()
        return generic_item 