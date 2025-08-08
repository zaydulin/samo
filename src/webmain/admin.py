from django.contrib import admin
from .models import *
import nested_admin
from django_ace import AceWidget
from django import forms


class GeneralSettingsForm(forms.ModelForm):
    message_header = forms.CharField(widget=AceWidget(mode='html',readonly=False,behaviours=True,showgutter=True,  wordwrap=False, usesofttabs=True))
    message_footer = forms.CharField(widget=AceWidget(mode='html',readonly=False,behaviours=True,showgutter=True,  wordwrap=False, usesofttabs=True))


class TestimonialInline(nested_admin.NestedTabularInline):
    model = Testimonial
    extra = 1


class ContactPageInline(nested_admin.NestedTabularInline):
    model = ContactPage
    extra = 1


class SeoInline(nested_admin.NestedTabularInline):
    model = Seo
    extra = 1


@admin.register(Categorys)
class CategorysAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "description"]
    prepopulated_fields = {"slug": ('name',), }
    list_display_links = ["id", "name", "description"]
    save_as = True
    save_on_top = True


@admin.register(Blogs)
class BlogsAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "slug"]
    prepopulated_fields = {"slug": ('name',), }
    list_display_links = ["id", "name", "slug"]
    save_as = True
    save_on_top = True


@admin.register(Pages)
class PagesAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "description"]
    prepopulated_fields = {"slug": ('name',), }
    list_display_links = ["id", "name", "description"]
    save_as = True
    save_on_top = True


@admin.register(Faqs)
class FaqsAdmin(admin.ModelAdmin):
    list_display = ["id", "question"]
    list_display_links = ["id", "question"]
    save_as = True
    save_on_top = True


class SettingsTemplateInline(nested_admin.NestedStackedInline):
    model = SettingsTemplate
    extra = 0
    max_num = 1
    min_num = 1


@admin.register(SettingsGlobale)
class SettingsGlobaleAdmin(nested_admin.NestedModelAdmin):
    inlines = [
        SettingsTemplateInline, ContactPageInline, SeoInline
    ]
    fieldsets = [
        ('Общие настройки', {
            'fields': [
                'logo', 'doplogo', 'site', 'paymentmetod',
                'favicon', 'description', 'name', 'content', 'message_header',
                'message_footer', 'yandex_metrica', 'google_analitic'
            ]
        }),
    ]
    list_display = ["id", "site", "name"]
    list_display_links = ["id", "site", "name"]


@admin.register(DocumentationsSite)
class DocumentationsSiteAdmin(admin.ModelAdmin):
    list_display = ["name"]

