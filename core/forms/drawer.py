from django import forms
from ..models.drawer import DrawerLineItem

class DrawerForm(forms.ModelForm):
    """Form for creating and editing drawers"""
    
    width = forms.DecimalField(
        min_value=0.001,
        max_digits=6,
        decimal_places=3,
        widget=forms.NumberInput(attrs={
            'step': '0.001',
            'class': 'form-control'
        })
    )
    
    height = forms.DecimalField(
        min_value=0.001,
        max_digits=6,
        decimal_places=3,
        widget=forms.NumberInput(attrs={
            'step': '0.001',
            'class': 'form-control'
        })
    )
    
    depth = forms.DecimalField(
        min_value=0.001,
        max_digits=6,
        decimal_places=3,
        widget=forms.NumberInput(attrs={
            'step': '0.001',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = DrawerLineItem
        fields = [
            'quantity', 
            'width', 
            'height', 
            'depth', 
            'wood_stock', 
            'bottom',
            'undermount',
            'finishing'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apply styling to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            
        # Add help text for dimension fields
        self.fields['width'].help_text = "Width in inches"
        self.fields['height'].help_text = "Height in inches"
        self.fields['depth'].help_text = "Depth in inches"
        
        # Set default quantity
        if not self.instance.pk:  # If it's a new drawer
            self.fields['quantity'].initial = 1
            
    def clean(self):
        cleaned_data = super().clean()
        width = cleaned_data.get('width')
        height = cleaned_data.get('height')
        depth = cleaned_data.get('depth')
        
        # Validate dimensions
        if width and width <= 0:
            self.add_error('width', "Width must be greater than zero")
        
        if height and height <= 0:
            self.add_error('height', "Height must be greater than zero")
            
        if depth and depth <= 0:
            self.add_error('depth', "Depth must be greater than zero")
            
        return cleaned_data 