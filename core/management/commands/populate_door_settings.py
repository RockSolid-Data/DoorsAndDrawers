"""
Management command to populate door settings data into the database.
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from core.models import (
    WoodStock,
    Design,
    PanelType,
    PanelRise,
    RailDefaults,
    Style,
    EdgeProfile,
    MiscellaneousDoorSettings,
)


class Command(BaseCommand):
    help = 'Populates the database with door settings data'

    def handle(self, *args, **options):
        self.stdout.write('Starting door settings population...\n')
        
        # Populate WoodStock
        self.populate_woodstock()
        
        # Populate Design
        self.populate_design()
        
        # Populate PanelType
        self.populate_panel_type()
        
        # Populate PanelRise
        self.populate_panel_rise()
        
        # Populate RailDefaults
        self.populate_rail_defaults()
        
        # Populate EdgeProfile
        self.populate_edge_profiles()
        
        # Populate Style (must come after PanelType and Design)
        self.populate_styles()
        
        # Populate MiscellaneousDoorSettings (must come after PanelType)
        self.populate_misc_settings()
        
        self.stdout.write(self.style.SUCCESS('\nDoor settings population completed!'))

    def populate_woodstock(self):
        """Populate WoodStock table with wood options and prices."""
        self.stdout.write('Populating WoodStock...')
        
        woodstock_data = [
            {'name': 'Alder', 'raised_panel_price': Decimal('7.50'), 'flat_panel_price': Decimal('7.00')},
            {'name': 'Ash', 'raised_panel_price': Decimal('5.00'), 'flat_panel_price': Decimal('4.50')},
            {'name': 'Basswood', 'raised_panel_price': Decimal('5.00'), 'flat_panel_price': Decimal('4.50')},
            {'name': 'Birch', 'raised_panel_price': Decimal('6.50'), 'flat_panel_price': Decimal('6.00')},
            {'name': 'Cherry', 'raised_panel_price': Decimal('8.50'), 'flat_panel_price': Decimal('8.00')},
            {'name': 'Cypress', 'raised_panel_price': Decimal('8.50'), 'flat_panel_price': Decimal('8.00')},
            {'name': 'Hickory', 'raised_panel_price': Decimal('6.50'), 'flat_panel_price': Decimal('6.00')},
            {'name': 'Mahogany', 'raised_panel_price': Decimal('9.50'), 'flat_panel_price': Decimal('9.00')},
            {'name': 'Red Oak', 'raised_panel_price': Decimal('5.00'), 'flat_panel_price': Decimal('4.50')},
        ]
        
        created_count = 0
        for data in woodstock_data:
            obj, created = WoodStock.objects.get_or_create(
                name=data['name'],
                defaults={
                    'raised_panel_price': data['raised_panel_price'],
                    'flat_panel_price': data['flat_panel_price'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'  Created: {obj.name}')
            else:
                self.stdout.write(f'  Already exists: {obj.name}')
        
        self.stdout.write(self.style.SUCCESS(f'  WoodStock: {created_count} created, {len(woodstock_data) - created_count} already existed'))

    def populate_design(self):
        """Populate Design table with door designs."""
        self.stdout.write('Populating Design...')
        
        design_data = [
            {'name': 'Crown', 'arch': True},
            {'name': 'Duncans', 'arch': True},
            {'name': 'French', 'arch': True},
            {'name': 'Heritage', 'arch': True},
            {'name': 'Oval', 'arch': True},
            {'name': 'Providential', 'arch': True},
            {'name': 'Square', 'arch': False},
        ]
        
        created_count = 0
        for data in design_data:
            obj, created = Design.objects.get_or_create(
                name=data['name'],
                defaults={'arch': data['arch']}
            )
            if created:
                created_count += 1
                self.stdout.write(f'  Created: {obj.name}')
            else:
                self.stdout.write(f'  Already exists: {obj.name}')
        
        self.stdout.write(self.style.SUCCESS(f'  Design: {created_count} created, {len(design_data) - created_count} already existed'))

    def populate_panel_type(self):
        """Populate PanelType table with panel types and surcharges."""
        self.stdout.write('Populating PanelType...')
        
        panel_type_data = [
            {
                'name': 'Drawer Front',
                'surcharge_width': Decimal('28.000'),
                'surcharge_height': Decimal('10.000'),
                'surcharge_percent': Decimal('15.0'),
                'minimum_sq_ft': Decimal('0.80'),
                'use_flat_panel_price': False,
            },
            {
                'name': 'Flat Panel',
                'surcharge_width': Decimal('22.000'),
                'surcharge_height': Decimal('39.000'),
                'surcharge_percent': Decimal('15.0'),
                'minimum_sq_ft': Decimal('2.00'),
                'use_flat_panel_price': True,
            },
            {
                'name': 'Frame Only',
                'surcharge_width': Decimal('22.000'),
                'surcharge_height': Decimal('39.000'),
                'surcharge_percent': Decimal('15.0'),
                'minimum_sq_ft': Decimal('2.00'),
                'use_flat_panel_price': True,
            },
            {
                'name': 'Raised Panel',
                'surcharge_width': Decimal('22.000'),
                'surcharge_height': Decimal('39.000'),
                'surcharge_percent': Decimal('15.0'),
                'minimum_sq_ft': Decimal('2.00'),
                'use_flat_panel_price': False,
            },
            {
                'name': 'Slab',
                'surcharge_width': Decimal('22.000'),
                'surcharge_height': Decimal('39.000'),
                'surcharge_percent': Decimal('15.0'),
                'minimum_sq_ft': Decimal('2.00'),
                'use_flat_panel_price': True,
            },
        ]
        
        created_count = 0
        for data in panel_type_data:
            obj, created = PanelType.objects.get_or_create(
                name=data['name'],
                defaults={
                    'surcharge_width': data['surcharge_width'],
                    'surcharge_height': data['surcharge_height'],
                    'surcharge_percent': data['surcharge_percent'],
                    'minimum_sq_ft': data['minimum_sq_ft'],
                    'use_flat_panel_price': data['use_flat_panel_price'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'  Created: {obj.name}')
            else:
                self.stdout.write(f'  Already exists: {obj.name}')
        
        self.stdout.write(self.style.SUCCESS(f'  PanelType: {created_count} created, {len(panel_type_data) - created_count} already existed'))

    def populate_panel_rise(self):
        """Populate PanelRise table with panel rise options."""
        self.stdout.write('Populating PanelRise...')
        
        panel_rise_data = [
            {'name': 'Panel Raise 1'},
            {'name': 'Panel Raise 2'},
            {'name': 'Panel Raise 3'},
        ]
        
        created_count = 0
        for data in panel_rise_data:
            obj, created = PanelRise.objects.get_or_create(name=data['name'])
            if created:
                created_count += 1
                self.stdout.write(f'  Created: {obj.name}')
            else:
                self.stdout.write(f'  Already exists: {obj.name}')
        
        self.stdout.write(self.style.SUCCESS(f'  PanelRise: {created_count} created, {len(panel_rise_data) - created_count} already existed'))

    def populate_rail_defaults(self):
        """Populate RailDefaults table with default rail sizes."""
        self.stdout.write('Populating RailDefaults...')
        
        # Check if RailDefaults already exists
        existing = RailDefaults.objects.first()
        
        if existing:
            self.stdout.write(f'  RailDefaults already exists (ID: {existing.id})')
            self.stdout.write(self.style.SUCCESS('  RailDefaults: 0 created, 1 already existed'))
        else:
            obj = RailDefaults.objects.create(
                top=Decimal('2.250'),
                bottom=Decimal('2.250'),
                left=Decimal('2.250'),
                right=Decimal('2.250'),
                interior_rail_size=Decimal('2.250'),
            )
            self.stdout.write(f'  Created RailDefaults (ID: {obj.id})')
            self.stdout.write(self.style.SUCCESS('  RailDefaults: 1 created, 0 already existed'))

    def populate_edge_profiles(self):
        """Populate EdgeProfile table with edge profile options."""
        self.stdout.write('Populating EdgeProfile...')
        
        edge_profile_data = ['E1', 'E2', 'E3', 'E4', 'E5']
        
        created_count = 0
        for name in edge_profile_data:
            obj, created = EdgeProfile.objects.get_or_create(name=name)
            if created:
                created_count += 1
                self.stdout.write(f'  Created: {obj.name}')
            else:
                self.stdout.write(f'  Already exists: {obj.name}')
        
        self.stdout.write(self.style.SUCCESS(f'  EdgeProfile: {created_count} created, {len(edge_profile_data) - created_count} already existed'))

    def populate_styles(self):
        """Populate Style table with door styles."""
        self.stdout.write('Populating Style...')
        
        # Get panel types and designs for foreign key references
        panel_types = {pt.name: pt for pt in PanelType.objects.all()}
        designs = {d.name: d for d in Design.objects.all()}
        
        # Check if required panel types and designs exist
        required_panel_types = ['Frame Only', 'Flat Panel', 'Raised Panel', 'Drawer Front']
        required_designs = ['Duncans', 'Crown', 'Square', 'Oval']
        
        missing_panel_types = [pt for pt in required_panel_types if pt not in panel_types]
        missing_designs = [d for d in required_designs if d not in designs]
        
        if missing_panel_types:
            self.stdout.write(self.style.WARNING(f'  Missing panel types: {missing_panel_types}. Run populate_panel_type first.'))
            return
        
        if missing_designs:
            self.stdout.write(self.style.WARNING(f'  Missing designs: {missing_designs}. Run populate_design first.'))
            return
        
        style_data = [
            {
                'name': 'ATFO',
                'panel_type': panel_types['Frame Only'],
                'design': designs['Duncans'],
                'price': Decimal('10.00'),
                'panels_across': 1,
                'panels_down': 1,
                'panel_overlap': Decimal('0.000'),
                'designs_on_top': True,
                'designs_on_bottom': False,
            },
            {
                'name': 'CTFP',
                'panel_type': panel_types['Flat Panel'],
                'design': designs['Crown'],
                'price': Decimal('10.00'),
                'panels_across': 1,
                'panels_down': 1,
                'panel_overlap': Decimal('0.250'),
                'designs_on_top': True,
                'designs_on_bottom': False,
            },
            {
                'name': 'CTFP-2x2',
                'panel_type': panel_types['Flat Panel'],
                'design': designs['Crown'],
                'price': Decimal('10.00'),
                'panels_across': 2,
                'panels_down': 2,
                'panel_overlap': Decimal('0.250'),
                'designs_on_top': True,
                'designs_on_bottom': False,
            },
            {
                'name': 'CTRP-2x3',
                'panel_type': panel_types['Raised Panel'],
                'design': designs['Crown'],
                'price': Decimal('14.00'),
                'panels_across': 2,
                'panels_down': 3,
                'panel_overlap': Decimal('0.312'),
                'designs_on_top': True,
                'designs_on_bottom': True,
            },
            {
                'name': 'CTRP-5P',
                'panel_type': panel_types['Raised Panel'],
                'design': designs['Crown'],
                'price': Decimal('14.00'),
                'panels_across': 5,
                'panels_down': 1,
                'panel_overlap': Decimal('0.312'),
                'designs_on_top': True,
                'designs_on_bottom': False,
            },
            {
                'name': 'DFDF',
                'panel_type': panel_types['Drawer Front'],
                'design': designs['Square'],
                'price': Decimal('3.50'),
                'panels_across': 1,
                'panels_down': 1,
                'panel_overlap': Decimal('0.000'),
                'designs_on_top': False,
                'designs_on_bottom': False,
            },
            {
                'name': 'OTFP-DP',
                'panel_type': panel_types['Flat Panel'],
                'design': designs['Oval'],
                'price': Decimal('10.00'),
                'panels_across': 1,
                'panels_down': 2,
                'panel_overlap': Decimal('0.250'),
                'designs_on_top': True,
                'designs_on_bottom': True,
            },
            {
                'name': 'SHAKER-FP-4P',
                'panel_type': panel_types['Flat Panel'],
                'design': designs['Square'],
                'price': Decimal('6.00'),
                'panels_across': 4,
                'panels_down': 1,
                'panel_overlap': Decimal('0.250'),
                'designs_on_top': False,
                'designs_on_bottom': False,
            },
        ]
        
        created_count = 0
        for data in style_data:
            obj, created = Style.objects.get_or_create(
                name=data['name'],
                defaults={
                    'panel_type': data['panel_type'],
                    'design': data['design'],
                    'price': data['price'],
                    'panels_across': data['panels_across'],
                    'panels_down': data['panels_down'],
                    'panel_overlap': data['panel_overlap'],
                    'designs_on_top': data['designs_on_top'],
                    'designs_on_bottom': data['designs_on_bottom'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'  Created: {obj.name}')
            else:
                self.stdout.write(f'  Already exists: {obj.name}')
        
        self.stdout.write(self.style.SUCCESS(f'  Style: {created_count} created, {len(style_data) - created_count} already existed'))

    def populate_misc_settings(self):
        """Populate MiscellaneousDoorSettings table with default settings."""
        self.stdout.write('Populating MiscellaneousDoorSettings...')
        
        # Check if MiscellaneousDoorSettings already exists
        existing = MiscellaneousDoorSettings.objects.first()
        
        if existing:
            self.stdout.write(f'  MiscellaneousDoorSettings already exists (ID: {existing.id})')
            self.stdout.write(self.style.SUCCESS('  MiscellaneousDoorSettings: 0 created, 1 already existed'))
        else:
            # Get panel types for drawer front and slab references
            drawer_front = PanelType.objects.filter(name='Drawer Front').first()
            slab = PanelType.objects.filter(name='Slab').first()
            
            if not drawer_front or not slab:
                self.stdout.write(self.style.WARNING('  Missing Drawer Front or Slab panel types. Run populate_panel_type first.'))
                return
            
            obj = MiscellaneousDoorSettings.objects.create(
                extra_height=Decimal('1.000'),
                extra_width=Decimal('0.500'),
                glue_min_width=Decimal('8.000'),
                rail_extra=Decimal('0.500'),
                drawer_front=drawer_front,
                drawer_slab=slab,
            )
            self.stdout.write(f'  Created MiscellaneousDoorSettings (ID: {obj.id})')
            self.stdout.write(self.style.SUCCESS('  MiscellaneousDoorSettings: 1 created, 0 already existed'))


