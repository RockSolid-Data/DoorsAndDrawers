from django import forms
from ..models import Order
from django.utils import timezone


class OrderForm(forms.ModelForm):
    is_quote = forms.BooleanField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.initial['order_date'] = timezone.localdate()

    class Meta:
        model = Order
        fields = [
            'customer',
            'billing_address1',
            'billing_address2',
            'order_date',
            'notes',
            'is_quote',
        ]
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'is_quote': forms.HiddenInput(),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.is_quote = self.cleaned_data.get('is_quote', False)
        if commit:
            instance.save()
        return instance