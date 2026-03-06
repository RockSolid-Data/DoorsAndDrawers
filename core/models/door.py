from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator

from .base import BaseModel
from .line_item import LineItem


class WoodStock(BaseModel):
    """Model for wood stock options (materials) for doors."""
    name = models.CharField(max_length=50, unique=True)
    raised_panel_price = models.DecimalField(max_digits=10, decimal_places=2)
    flat_panel_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.name


class Design(BaseModel):
    """Model for door designs."""
    name = models.CharField(max_length=50, unique=True)
    arch = models.BooleanField(default=False)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Additional design charge (e.g., Arched=$5)"
    )
    
    def __str__(self):
        return self.name


class EdgeProfile(BaseModel):
    """Model for door edge profiles."""
    name = models.CharField(max_length=10, unique=True)  # E1, E2, etc.
    
    def __str__(self):
        return self.name


class PanelType(BaseModel):
    """Model for door panel types."""
    name = models.CharField(max_length=50, unique=True)
    design_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Design charge for this panel type (e.g., Raised=$10, Flat=$6, Slab=$3.50)"
    )
    surcharge_width = models.DecimalField(max_digits=5, decimal_places=2)
    surcharge_height = models.DecimalField(max_digits=5, decimal_places=2)
    surcharge_percent = models.DecimalField(max_digits=5, decimal_places=2)
    minimum_sq_ft = models.DecimalField(max_digits=5, decimal_places=2)
    use_flat_panel_price = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class PanelRise(BaseModel):
    """Model for panel rise options."""
    name = models.CharField(max_length=50, unique=True)
    surcharge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Additional surcharge for this panel rise (e.g., Glaze=$2)"
    )
    
    def __str__(self):
        return self.name


class Style(BaseModel):
    """Model for door styles."""
    name = models.CharField(max_length=50, unique=True)  # ATFP, CTF, etc.
    panel_type = models.ForeignKey(PanelType, on_delete=models.PROTECT)
    design = models.ForeignKey(Design, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    panels_across = models.PositiveSmallIntegerField(default=1)
    panels_down = models.PositiveSmallIntegerField(default=1)
    panel_overlap = models.DecimalField(max_digits=5, decimal_places=3)
    designs_on_top = models.BooleanField(default=False)
    designs_on_bottom = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.panel_type.name} - {self.design.name}"


class DoorLineItem(LineItem):
    """Model for door line items with all settings."""
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='door_items',
        verbose_name="Order"
    )
    
    wood_stock = models.ForeignKey(WoodStock, on_delete=models.PROTECT)
    edge_profile = models.ForeignKey(EdgeProfile, on_delete=models.PROTECT)
    panel_rise = models.ForeignKey(PanelRise, on_delete=models.PROTECT, null=True, blank=True)
    style = models.ForeignKey(Style, on_delete=models.PROTECT)

    # Door dimensions
    width = models.DecimalField(
        max_digits=10, 
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Width in inches"
    )
    height = models.DecimalField(
        max_digits=10, 
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Height in inches"
    )
    
    # Rail dimensions
    rail_top = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Top rail size in inches",
        default=Decimal('1.000')
    )
    rail_bottom = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Bottom rail size in inches",
        default=Decimal('1.000')
    )
    rail_left = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Left rail size in inches",
        default=Decimal('1.000')
    )
    rail_right = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Right rail size in inches",
        default=Decimal('1.000')
    )
    interior_rail_size = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Interior rail size in inches",
        default=Decimal('1.000')
    )

    # Sanding options
    sand_edge = models.BooleanField(
        default=False,
        help_text="Whether to sand the edges of the door"
    )
    sand_cross_grain = models.BooleanField(
        default=False,
        help_text="Whether to sand across the grain"
    )
    
    class Meta:
        verbose_name = "Door Item"
        verbose_name_plural = "Door Items"
    
    @property
    def square_feet(self):
        """Calculate the square footage of the door, enforcing minimum from panel type."""
        sq_ft = (self.width * self.height) / Decimal('144')
        min_sq_ft = self.style.panel_type.minimum_sq_ft
        if min_sq_ft and sq_ft < min_sq_ft:
            sq_ft = min_sq_ft
        return sq_ft

    def calculate_price(self):
        """Calculate the unit price based on door specifications.

        Formula: Design Charge + (Square Feet x Material Cost per sq ft)
                 + oversize surcharge (if applicable)
                 + panel rise surcharge (if applicable)
        """
        panel_type = self.style.panel_type

        # Material cost per sq ft from wood stock
        if panel_type.use_flat_panel_price:
            material_cost = self.wood_stock.flat_panel_price
        else:
            material_cost = self.wood_stock.raised_panel_price

        # Design charge from panel type + design
        design_charge = panel_type.design_charge + self.style.design.price

        # Base price = design charge + (sq ft x material cost)
        price = design_charge + (self.square_feet * material_cost)

        # Oversize surcharge: if width or height exceeds threshold, apply percentage
        if panel_type.surcharge_percent and (
            (panel_type.surcharge_width and self.width > panel_type.surcharge_width)
            or (panel_type.surcharge_height and self.height > panel_type.surcharge_height)
        ):
            price *= (1 + panel_type.surcharge_percent / Decimal('100'))

        # Panel rise surcharge
        if self.panel_rise and self.panel_rise.surcharge:
            price += self.panel_rise.surcharge

        return price.quantize(Decimal('0.01'))
    
    def __str__(self):
        return f"Door {self.id} - {self.wood_stock.name} {self.style.name}"

    def save(self, *args, **kwargs):
        # Always set type to 'door'
        self.type = 'door'
        # Call the parent save method to handle price calculations
        super().save(*args, **kwargs)


class RailDefaults(BaseModel):
    """Model for default rail sizes for doors."""
    top = models.DecimalField(
        max_digits=5, 
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Default top rail size in inches"
    )
    bottom = models.DecimalField(
        max_digits=5, 
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Default bottom rail size in inches"
    )
    left = models.DecimalField(
        max_digits=5, 
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Default left rail size in inches"
    )
    right = models.DecimalField(
        max_digits=5, 
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Default right rail size in inches"
    )
    interior_rail_size = models.DecimalField(
        max_digits=5, 
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Default interior rail size in inches"
    )
    
    class Meta:
        verbose_name = "Rail Defaults"
        verbose_name_plural = "Rail Defaults"
    
    def __str__(self):
        return f"Rail Defaults: T:{self.top}, B:{self.bottom}, L:{self.left}, R:{self.right}, I:{self.interior_rail_size}"


class MiscellaneousDoorSettings(BaseModel):
    """Model for miscellaneous door settings and defaults."""
    extra_height = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Extra height to add when gluing sheet"
    )
    extra_width = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Extra width to add when gluing sheet"
    )
    glue_min_width = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Minimum width for gluing sheet"
    )
    rail_extra = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Rail joint extra"
    )
    drawer_front = models.ForeignKey(
        PanelType,
        on_delete=models.PROTECT,
        related_name='drawer_front_settings',
        help_text="Panel type to use for drawer fronts"
    )
    drawer_slab = models.ForeignKey(
        PanelType,
        on_delete=models.PROTECT,
        related_name='drawer_slab_settings',
        help_text="Panel type to use for drawer slabs"
    )

    class Meta:
        verbose_name = "Miscellaneous Door Settings"
        verbose_name_plural = "Miscellaneous Door Settings"

    def __str__(self):
        return f"Door Settings (Extra H:{self.extra_height}, W:{self.extra_width})"