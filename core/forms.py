from django import forms
from .models import Contact


class CheckoutForm(forms.Form):
    street_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': '1234 main str',
        'class': 'form-control'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Apartment or Suite',
        'class': 'form-control'
    }))
    phone_number = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Phone Number',
        'class': 'form-control'
    }))
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'mail', 'subject', 'message')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter your name', 'class': 'contact-input'}),
            'mail': forms.TextInput(attrs={'placeholder': 'Enter your mail', 'class': 'contact-input'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Subject', 'class': 'contact-input'}),
            'message': forms.TextInput(attrs={'placeholder': 'Enter your message', 'class': 'contact-textarea contact-input'})
        }
