from django import forms
from .models import Laptop, Store, Review

class LaptopForm(forms.ModelForm):
    class Meta:
        model = Laptop
        fields = ['name', 'screen_size', 'price', 'processor', 'graphics_card', 'ram', 'storage', 'url']

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['title']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment']