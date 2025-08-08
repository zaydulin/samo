from django import forms
from moderation.models import  Applications
from django.contrib.auth.models import User


# class SubscriptionForm(forms.ModelForm):
#     email = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'placeholder': 'Email',  'name':'emailaddress', 'id': 'profile-email', 'class':'form-control'}))
#
#     class Meta:
#         model = Subscriptions
#         fields = ['email',]

class CompanyEmailForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))


class CooperationForm(forms.ModelForm):
    type = forms.ChoiceField(choices=Applications.TYPE, initial=4, widget=forms.HiddenInput())

    class Meta:
        model = Applications
        fields = ['type', 'user', 'email', 'phone', 'content', 'company_name', 'company_inn', 'company_director', 'company_adress',  'company_description']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Телефон'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название компании'}),
            'company_inn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ИНН организации или ИП'}),
            'company_director': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ФИО директора'}),
            'company_adress': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Адрес'}),
            'company_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Описание'}),
            'type': forms.HiddenInput(),
        }
class PartnershipForm(forms.ModelForm):
    type = forms.ChoiceField(choices=Applications.TYPE, initial=3, widget=forms.HiddenInput())

    class Meta:
        model = Applications
        fields = ['type', 'user', 'email', 'phone', 'content']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Телефон'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Описание'}),
            'type': forms.HiddenInput(),
        }