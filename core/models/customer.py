from django.db import models
from .base import BaseModel
from ..utils import get_us_states

class Customer(BaseModel):
    company_name = models.CharField(
        max_length=255,
        verbose_name="Company Name",
        blank=True,
        null=True
    )
    first_name = models.CharField(
        max_length=255,
        verbose_name="First Name",
        blank=True,
        null=True
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name="Last Name",
        blank=True,
        null=True
    )
    taxable = models.BooleanField(
        default=False,
        verbose_name="Taxable",
        help_text="Whether this customer should be charged tax on orders"
    )
    address_line1 = models.CharField(
        max_length=255,
        verbose_name="Address Line 1",
        blank=True,
        null=True
    )
    address_line2 = models.CharField(
        max_length=255,
        verbose_name="Address Line 2",
        blank=True,
        null=True
    )
    city = models.CharField(
        max_length=255,
        verbose_name="City",
        blank=True,
        null=True
    )
    state = models.CharField(
        max_length=2,
        choices=get_us_states(),
        verbose_name="State",
        blank=True,
        null=True
    )
    zip_code = models.CharField(
        max_length=5,
        verbose_name="ZIP Code",
        blank=True,
        null=True
    )
    phone = models.CharField(
        max_length=10,
        verbose_name="Phone Number",
        blank=True,
        null=True
    )
    fax = models.CharField(
        max_length=10,
        verbose_name="Fax Number",
        blank=True,
        null=True
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes"
    )
    
    # Add JSON fields for door and drawer defaults
    door_defaults = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Door default preferences for this customer"
    )
    
    drawer_defaults = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Drawer default preferences for this customer"
    )

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        company = self.company_name.title() if self.company_name else "No Company"
        first = self.first_name.capitalize() if self.first_name else ""
        last = self.last_name.capitalize() if self.last_name else ""
        name = f"{first} {last}".strip() if first or last else "No Name"
        return f"{company} - {name}"

    @property
    def quotes(self):
        """Return only quotes for this customer"""
        return self.orders.filter(is_quote=True)

    @property
    def confirmed_orders(self):
        """Return only confirmed orders for this customer"""
        return self.orders.filter(is_quote=False)

    def save(self, *args, **kwargs):
        # Convert names to lowercase if they exist
        if self.company_name:
            self.company_name = self.company_name.lower()
        if self.first_name:
            self.first_name = self.first_name.lower()
        if self.last_name:
            self.last_name = self.last_name.lower()
        if self.city:
            self.city = self.city.lower()
        if self.address_line1:
            self.address_line1 = self.address_line1.lower()
        if self.address_line2:
            self.address_line2 = self.address_line2.lower()
        if self.notes:
            self.notes = self.notes.lower()

        # Strip any formatting from phone/fax if they exist
        if self.phone:
            if not self.phone.isdigit():
                self.phone = ''.join(filter(str.isdigit, self.phone))
        if self.fax:
            if not self.fax.isdigit():
                self.fax = ''.join(filter(str.isdigit, self.fax))
        super().save(*args, **kwargs)
    
    def get_door_defaults(self):
        """
        Get door defaults for this customer.
        Returns only customer-specific defaults from the JSON field.
        Filters out rail dimensions that match the global defaults.
        """
        if not self.door_defaults:
            return {}
            
        # Get a copy of the defaults
        defaults = self.door_defaults.copy()
        
        # Get global rail defaults to filter out matching values
        from .door import RailDefaults
        global_rail_defaults = RailDefaults.objects.first()
        
        if global_rail_defaults:
            # Check each rail dimension and remove it if it matches the global default
            rail_fields = {
                'rail_top': 'top',
                'rail_bottom': 'bottom',
                'rail_left': 'left',
                'rail_right': 'right',
                'interior_rail_size': 'interior_rail_size'
            }
            
            for customer_field, global_field in rail_fields.items():
                if customer_field in defaults:
                    try:
                        # Compare the customer value with the global default
                        from decimal import Decimal
                        customer_value = Decimal(str(defaults[customer_field]))
                        global_value = getattr(global_rail_defaults, global_field)
                        
                        # If they match, remove the customer-specific override
                        if customer_value == global_value:
                            defaults.pop(customer_field)
                    except (ValueError, TypeError, AttributeError):
                        # Keep the value if there's any error in comparison
                        pass
                        
        return defaults
    
    def get_drawer_defaults(self):
        """
        Get drawer defaults for this customer.
        Returns only customer-specific defaults from the JSON field.
        """
        # Simply return the drawer defaults as is
        return self.drawer_defaults.copy() if self.drawer_defaults else {}
            
    def set_door_defaults(self, **kwargs):
        """
        Set door defaults for this customer.
        Accepts keyword arguments for door properties.
        If a value is None, it will remove that key from door_defaults.
        """
        # Convert model instances to IDs for JSON serialization
        for key, value in list(kwargs.items()):
            if value is None:
                # Remove this key from door_defaults
                if key in self.door_defaults:
                    self.door_defaults.pop(key)
                # Remove from kwargs to avoid storing None values
                kwargs.pop(key)
            elif hasattr(value, 'pk'):
                kwargs[key] = value.pk
                
        # Update the door_defaults field with remaining values
        if not self.door_defaults:
            self.door_defaults = {}
            
        self.door_defaults.update(kwargs)
        self.save(update_fields=['door_defaults'])
        
    def set_drawer_defaults(self, **kwargs):
        """
        Set drawer defaults for this customer.
        Accepts keyword arguments for drawer properties.
        If a value is None, it will remove that key from drawer_defaults.
        """
        # Convert model instances to IDs for JSON serialization
        for key, value in list(kwargs.items()):
            if value is None:
                # Remove this key from drawer_defaults
                if key in self.drawer_defaults:
                    self.drawer_defaults.pop(key)
                # Remove from kwargs to avoid storing None values
                kwargs.pop(key)
            elif hasattr(value, 'pk'):
                kwargs[key] = value.pk
                
        # Update the drawer_defaults field
        if not self.drawer_defaults:
            self.drawer_defaults = {}
            
        self.drawer_defaults.update(kwargs)
        self.save(update_fields=['drawer_defaults'])

class CustomerDefaults(BaseModel):
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name='defaults'
    )
    discount_type = models.CharField(
        max_length=10,
        choices=[
            ('PERCENT', 'Percentage'),
            ('FIXED', 'Fixed Amount')
        ],
        default='PERCENT',
        verbose_name="Discount Type"
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Discount Value"
    )
    surcharge_type = models.CharField(
        max_length=10,
        choices=[
            ('PERCENT', 'Percentage'),
            ('FIXED', 'Fixed Amount')
        ],
        default='PERCENT',
        verbose_name="Surcharge Type"
    )
    surcharge_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Surcharge Value"
    )
    shipping_type = models.CharField(
        max_length=10,
        choices=[
            ('PERCENT', 'Percentage'),
            ('FIXED', 'Fixed Amount')
        ],
        default='PERCENT',
        verbose_name="Shipping Type"
    )
    shipping_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Shipping Value"
    )

    class Meta:
        verbose_name = "Customer Default"
        verbose_name_plural = "Customer Defaults"

    def __str__(self):
        return f"Defaults for {self.customer}"

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validate percentage values are between 0 and 100
        if self.discount_type == 'PERCENT' and self.discount_value > 100:
            raise ValidationError("Percentage discount cannot exceed 100%")
        if self.surcharge_type == 'PERCENT' and self.surcharge_value > 100:
            raise ValidationError("Percentage surcharge cannot exceed 100%")
        if self.shipping_type == 'PERCENT' and self.shipping_value > 100:
            raise ValidationError("Percentage shipping charge cannot exceed 100%")

    def get_formatted_discount(self):
        """Return formatted string of discount"""
        if self.discount_type == 'PERCENT':
            return f"{self.discount_value}%"
        return f"${self.discount_value}"

    def get_formatted_surcharge(self):
        """Return formatted string of surcharge"""
        if self.surcharge_type == 'PERCENT':
            return f"{self.surcharge_value}%"
        return f"${self.surcharge_value}"

    def get_formatted_shipping(self):
        """Return formatted string of shipping"""
        if self.shipping_type == 'PERCENT':
            return f"{self.shipping_value}%"
        return f"${self.shipping_value}" 