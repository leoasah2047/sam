import django_filters
from django_filters import CharFilter
from django.forms.widgets import TextInput
from .models import *


class ItemFilter(django_filters.FilterSet):
    category = CharFilter(field_name='category', lookup_expr='icontains', widget=TextInput(attrs={
        'placeholder': 'Search Category',
        'class': 'inputx'
    }))

    class Meta:
        model = Item
        fields = ['title', 'category', 'label']
