from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from .base import BaseModel
from .line_item import LineItem

class DrawerWoodStock(BaseModel):
    """Wood stock options for drawers"""
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Drawer Wood Stock'
        verbose_name_plural = 'Drawer Wood Stocks'

class DrawerBottomSize(BaseModel):
    """Bottom material types for drawers"""
    name = models.CharField(max_length=100, unique=True)
    thickness = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        default=1.000,
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Drawer Bottom Type'
        verbose_name_plural = 'Drawer Bottom Types'

class DrawerPricing(BaseModel):
    """Base pricing configuration for drawers"""
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=50.00,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    class Meta:
        verbose_name = 'Drawer Pricing'
        verbose_name_plural = 'Drawer Pricing'
    
    def __str__(self):
        return f"Drawer Pricing Configuration (ID: {self.id})"

class DrawerDimensionSurcharge(BaseModel):
    """Dimension-based surcharge tiers for drawers.
    Each row defines a width and depth threshold plus a surcharge percentage.
    If a drawer's width OR depth exceeds the threshold, the row matches.
    Among all matching rows, only the highest surcharge_percent is applied.
    """
    width = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        help_text="Width threshold in inches",
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    depth = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        help_text="Depth threshold in inches",
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    surcharge_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage surcharge applied when threshold is exceeded",
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    class Meta:
        ordering = ['surcharge_percent']
        verbose_name = 'Drawer Dimension Surcharge'
        verbose_name_plural = 'Drawer Dimension Surcharges'

    def __str__(self):
        return f"W>{self.width}″ / D>{self.depth}″ → {self.surcharge_percent}%"


class DrawerLineItem(LineItem):
    """Drawer line item model"""
    # Override the order field to use a specific related_name
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='drawer_items',
        verbose_name="Order"
    )
    
    # Dimensions
    width = models.DecimalField(
        max_digits=6, 
        decimal_places=3,
        help_text="Width in inches"
    )
    height = models.DecimalField(
        max_digits=6, 
        decimal_places=3,
        help_text="Height in inches"
    )
    depth = models.DecimalField(
        max_digits=6, 
        decimal_places=3,
        help_text="Depth in inches"
    )
    
    # Materials
    wood_stock = models.ForeignKey(
        DrawerWoodStock,
        on_delete=models.PROTECT,
        related_name='drawer_items'
    )
    bottom = models.ForeignKey(
        DrawerBottomSize,
        on_delete=models.PROTECT,
        related_name='drawer_items'
    )
    
    # Options
    undermount = models.BooleanField(
        default=False,
        help_text="Whether drawer uses undermount slides"
    )
    finishing = models.BooleanField(
        default=False,
        help_text="Whether drawer requires finishing"
    )
    
    class Meta:
        verbose_name = 'Drawer'
        verbose_name_plural = 'Drawers'
    
    def __str__(self):
        return f"{self.width}″ × {self.height}″ × {self.depth}″ Drawer"
    
    def calculate_price(self):
        """Calculate the unit price of the drawer based on dimensions and options.

        Formula: DrawerPricing tier base (by height)
                 + WoodStock price + Bottom price
                 + Undermount charge (if selected) + Finish charge (if selected)
                 then x (1 + highest matching surcharge_percent/100) if oversized
        """
        tier = DrawerPricing.objects.filter(
            height__gte=self.height
        ).order_by('height').first()
        if tier is None:
            tier = DrawerPricing.objects.order_by('-height').first()
        tier_price = tier.price if tier else Decimal('0.00')

        price = tier_price + self.wood_stock.price + self.bottom.price

        default_settings = DefaultDrawerSettings.objects.first()
        if default_settings:
            if self.undermount:
                price += default_settings.undermount_charge
            if self.finishing:
                price += default_settings.finish_charge

        from django.db.models import Q
        matching = DrawerDimensionSurcharge.objects.filter(
            Q(width__gt=0, width__lte=self.width) | Q(depth__gt=0, depth__lte=self.depth)
        ).order_by('-surcharge_percent').first()

        if matching:
            price *= (1 + matching.surcharge_percent / Decimal('100'))

        return price.quantize(Decimal('0.01'))
    
    def save(self, *args, **kwargs):
        # Always set type to 'drawer'
        self.type = 'drawer'
        # Call the parent save method to handle price calculations
        super().save(*args, **kwargs) 

class DefaultDrawerSettings(BaseModel):
    """Default settings and pricing adjustments for drawers"""
    finish_charge = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Additional charge for finishing",
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    undermount_charge = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Additional charge for undermount slides",
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    ends_cutting_adjustment = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        default=0.000,
        help_text="Adjustment for cutting drawer ends",
        validators=[MinValueValidator(Decimal('0.000'))]
    )
    sides_cutting_adjustment = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        default=0.000,
        help_text="Adjustment for cutting drawer sides",
        validators=[MinValueValidator(Decimal('0.000'))]
    )
    plywood_size_adjustment = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        default=0.000,
        help_text="Adjustment for plywood sizing",
        validators=[MinValueValidator(Decimal('0.000'))]
    )
    
    class Meta:
        verbose_name = 'Default Drawer Settings'
        verbose_name_plural = 'Default Drawer Settings'
    
    def __str__(self):
        return f"Default Drawer Settings (ID: {self.id})" 