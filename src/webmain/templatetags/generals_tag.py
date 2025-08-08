from django import template
from webmain.models import SettingsGlobale, ContactPage, Pages
from webmain.forms import CompanyEmailForm
from django.shortcuts import render
register = template.Library()





@register.inclusion_tag('site/registration_form.html')
def company_signup_form():
    form = CompanyEmailForm()
    return {'form': form}

@register.simple_tag
def get_settings_first():
    return SettingsGlobale.objects.first()


@register.simple_tag
def get_contacts_first():
    return ContactPage.objects.first()

@register.simple_tag
def get_pages():
    return Pages.objects.all()