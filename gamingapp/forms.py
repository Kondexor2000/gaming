from django import forms
from .models import Laptop, Store

class LaptopForm(forms.ModelForm):
    class Meta:
        model = Laptop
        fields = ['name', 'cale', 'price', 'processor', 'graphics_card', 'ram', 'rom', 'url']

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['title']