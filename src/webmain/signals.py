from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction
from .models import Seo, SettingsGlobale, SettingsTemplate, ContactPage
from integration_payment.models import PaymentType
import os
from django.conf import settings
import asyncio
import threading


@receiver(post_save, sender=PaymentType)
def ensure_unique_turn_on(sender, instance, created, **kwargs):
    if instance.turn_on:
        with transaction.atomic():
            other_types = PaymentType.objects.filter(type=instance.type, turn_on=True).exclude(id=instance.id)

            for other_type in other_types:
                other_type.turn_on = False
                other_type.save()

@receiver(post_save, sender=Seo)
def assign_site_to_seo(sender, instance, created, **kwargs):
    if created and instance.setting and instance.setting.site:
        instance.site = instance.setting.site
        instance.save()


@receiver(post_save, sender=SettingsTemplate)
def update_domainmixin_file(sender, instance, created, **kwargs):
    def update_file_async():
        try:
            file_path = os.path.join(settings.BASE_DIR, '_project', 'domainsmixin.py')

            # Получение всех настроек
            all_settings = SettingsTemplate.objects.all()
            new_domain_templates = {setting.site.domain: f'{setting.templates}/' for setting in all_settings}



            # Чтение текущего содержимого файла
            try:
                with open(file_path, 'r') as file:
                    current_content = file.read()

            except FileNotFoundError:
                current_content = ''


            # Извлечение текущих значений
            try:
                if 'domain_templates = {' in current_content:
                    start_idx = current_content.index('domain_templates = {') + len('domain_templates = {')
                    end_idx = current_content.index('}', start_idx)
                    current_templates_str = current_content[start_idx:end_idx].strip()
                    current_domain_templates = dict(
                        item.split(': ') for item in current_templates_str.split(',\n    ')
                    )

                else:
                    current_domain_templates = {}

            except (ValueError, KeyError):
                current_domain_templates = {}


            # Определение новых и обновленных значений
            updated_domain_templates = {domain: template for domain, template in new_domain_templates.items()
                                        if current_domain_templates.get(domain) != template}


            # Формирование нового содержимого файла
            domain_templates_str = ',\n    '.join([
                f"'{domain}': '{template}'" for domain, template in new_domain_templates.items()
            ])
            new_file_content = f"""
                class DomainTemplateMixin:
                    def get_template_names(self):
                        current_domain = self.request.get_host()
                        template_name = 'default/'  # Default template name
                
                        # Define templates for different domains
                        domain_templates = {{
                            {domain_templates_str}
                        }}
                
                        if current_domain in domain_templates:
                            template_name = domain_templates[current_domain]
                
                        return [f'site/{{template_name}}{{self.template_name}}.html']
                
                    def get_queryset(self):
                        # Override this method in each view to filter the appropriate content
                        pass
                """

            # Сравнение содержимого и запись
            if current_content.strip() != new_file_content.strip():
                with open(file_path, 'w') as file:
                    file.write(new_file_content.strip())
            else: pass


        except Exception as e:
            pass

    # Запуск обновления файла в отдельном потоке
    thread = threading.Thread(target=update_file_async)
    thread.start()





@receiver(pre_save, sender=SettingsTemplate)
def update_site_from_setting_template(sender, instance, **kwargs):
    if instance.setting:
        instance.site = instance.setting.site


@receiver(pre_save, sender=ContactPage)
def update_site_from_setting_contact(sender, instance, **kwargs):
    if instance.setting:
        instance.site = instance.setting.site
