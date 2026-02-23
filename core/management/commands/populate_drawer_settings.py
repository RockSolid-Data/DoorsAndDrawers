"""
Management command to populate drawer settings data into the database.
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from core.models import (
    DrawerWoodStock,
    DrawerBottomSize,
    DrawerPricing,
    DefaultDrawerSettings,
)


class Command(BaseCommand):
    help = 'Populates the database with drawer settings data'

    def handle(self, *args, **options):
        self.stdout.write('Starting drawer settings population...\n')
        
        # Populate DrawerWoodStock
        self.populate_drawer_woodstock()
        
        # Populate DrawerBottomSize
        self.populate_drawer_bottom_size()
        
        # Populate DrawerPricing
        self.populate_drawer_pricing()
        
        # Populate DefaultDrawerSettings
        self.populate_default_drawer_settings()
        
        self.stdout.write(self.style.SUCCESS('\nDrawer settings population completed!'))

    def populate_drawer_woodstock(self):
        """Populate DrawerWoodStock table with wood options."""
        self.stdout.write('Populating DrawerWoodStock...')
        
        # Using default price of $1.00 for all wood types
        woodstock_data = [
            {'name': 'Birch', 'price': Decimal('1.00')},
            {'name': 'Cedar', 'price': Decimal('1.00')},
            {'name': 'Cherry', 'price': Decimal('1.00')},
            {'name': 'Hickory', 'price': Decimal('1.00')},
            {'name': 'Maple', 'price': Decimal('1.00')},
            {'name': 'Oak', 'price': Decimal('1.00')},
            {'name': 'Poplar', 'price': Decimal('1.00')},
        ]
        
        created_count = 0
        for data in woodstock_data:
            obj, created = DrawerWoodStock.objects.get_or_create(
                name=data['name'],
                defaults={'price': data['price']}
            )
            if created:
                created_count += 1
                self.stdout.write(f'  Created: {obj.name}')
            else:
                self.stdout.write(f'  Already exists: {obj.name}')
        
        self.stdout.write(self.style.SUCCESS(f'  DrawerWoodStock: {created_count} created, {len(woodstock_data) - created_count} already existed'))

    def populate_drawer_bottom_size(self):
        """Populate DrawerBottomSize table with bottom sizes and prices."""
        self.stdout.write('Populating DrawerBottomSize...')
        
        bottom_size_data = [
            {'name': '1/4 inch', 'thickness': Decimal('0.250'), 'price': Decimal('1.00')},
            {'name': '3/8 Inch', 'thickness': Decimal('0.375'), 'price': Decimal('3.00')},
        ]
        
        created_count = 0
        for data in bottom_size_data:
            obj, created = DrawerBottomSize.objects.get_or_create(
                name=data['name'],
                defaults={
                    'thickness': data['thickness'],
                    'price': data['price'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'  Created: {obj.name}')
            else:
                self.stdout.write(f'  Already exists: {obj.name}')
        
        self.stdout.write(self.style.SUCCESS(f'  DrawerBottomSize: {created_count} created, {len(bottom_size_data) - created_count} already existed'))

    def populate_drawer_pricing(self):
        """Populate DrawerPricing table with height-based pricing tiers."""
        self.stdout.write('Populating DrawerPricing...')
        
        pricing_data = [
            {'height': Decimal('3.250'), 'price': Decimal('15.00')},
            {'height': Decimal('4.250'), 'price': Decimal('17.00')},
            {'height': Decimal('5.250'), 'price': Decimal('19.00')},
            {'height': Decimal('6.250'), 'price': Decimal('21.00')},
            {'height': Decimal('7.250'), 'price': Decimal('24.00')},
            {'height': Decimal('8.250'), 'price': Decimal('27.00')},
            {'height': Decimal('9.250'), 'price': Decimal('31.00')},
        ]
        
        created_count = 0
        for data in pricing_data:
            obj, created = DrawerPricing.objects.get_or_create(
                height=data['height'],
                defaults={'price': data['price']}
            )
            if created:
                created_count += 1
                self.stdout.write(f'  Created: Height {obj.height}" = ${obj.price}')
            else:
                self.stdout.write(f'  Already exists: Height {obj.height}"')
        
        self.stdout.write(self.style.SUCCESS(f'  DrawerPricing: {created_count} created, {len(pricing_data) - created_count} already existed'))

    def populate_default_drawer_settings(self):
        """Populate DefaultDrawerSettings table with default settings."""
        self.stdout.write('Populating DefaultDrawerSettings...')
        
        # Check if DefaultDrawerSettings already exists
        existing = DefaultDrawerSettings.objects.first()
        
        if existing:
            self.stdout.write(f'  DefaultDrawerSettings already exists (ID: {existing.id})')
            self.stdout.write(self.style.SUCCESS('  DefaultDrawerSettings: 0 created, 1 already existed'))
        else:
            obj = DefaultDrawerSettings.objects.create(
                surcharge_width=Decimal('24.000'),
                surcharge_depth=Decimal('24.000'),
                surcharge_percent=Decimal('15.00'),
                finish_charge=Decimal('9.00'),
                undermount_charge=Decimal('2.50'),
                ends_cutting_adjustment=Decimal('0.000'),
                sides_cutting_adjustment=Decimal('-0.375'),
                plywood_size_adjustment=Decimal('-0.750'),
            )
            self.stdout.write(f'  Created DefaultDrawerSettings (ID: {obj.id})')
            self.stdout.write(self.style.SUCCESS('  DefaultDrawerSettings: 1 created, 0 already existed'))






