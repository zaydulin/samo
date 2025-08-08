from django.contrib import admin
from django.utils.html import format_html
from .models import *
import nested_admin

# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['phone', 'display_avatar', 'get_type_display', 'username']
    list_display_links = ['phone', 'display_avatar', 'get_type_display', 'username']

    def display_avatar(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" alt="{}" height="100" />', obj.avatar.url, obj.username)
        return ''

    display_avatar.short_description = 'Аватарка'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['get_status_display', 'user']


class ChatMessageMediaInline(nested_admin.NestedTabularInline):
    model = ChatMessageMedia
    extra = 1


class ChatMessageInline(nested_admin.NestedTabularInline):
    model = ChatMessage
    extra = 1
    inlines = [ChatMessageMediaInline]

    # Удаляем поле `author` из формы редактирования
    # def get_formset(self, request, obj=None, **kwargs):
    #     formset = super().get_formset(request, obj, **kwargs)
    #     formset.form.base_fields.pop('author', None)  # Скрываем поле `author` в inline
    #     formset.form.base_fields.pop('ftp_access_message', None)  # Hide the 'ftp_access_message' field
    #     return formset
    #
    # def get_readonly_fields(self, request, obj=None):
    #     if obj:  # Если объект существует, делаем его только для чтения
    #         return ['author', 'ticket']
    #     return []
    #
    # def has_change_permission(self, request, obj=None):
    #     if obj:
    #         return False  # Запрет на изменение существующих объектов
    #     return True  # Разрешить изменение новых объектов
    #
    # def has_delete_permission(self, request, obj=None):
    #     if obj:
    #         return False  # Запрет на удаление существующих объектов
    #     return True  # Разрешить удаление новых объектов


# Admin для `Ticket`
@admin.register(Chat)
class ChatAdmin(nested_admin.NestedModelAdmin):
    list_display = ['owner']
    list_filter = ['owner']
    inlines = [ChatMessageInline]

    # # Только для чтения поля для `Ticket`, без поля `author`
    # readonly_fields = ()  # Убедитесь, что нет полей, которые вызовут ошибки
    # # Метод для исключения полей из формы
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     return form
    #
    # def get_readonly_fields(self, request, obj=None):
    #     if obj:  # When editing an existing object
    #         return self.readonly_fields + ('owner',)
    #     return self.readonly_fields



@admin.register(Notificationgroups)
class NotificationgroupsAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'object_id']

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'object_id']

admin.site.register(UserSessionBridge)
admin.site.register(UserSession)
admin.site.register(Schedule)
admin.site.register(History)