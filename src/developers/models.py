from django.db import models
from django.conf import settings
import os
from django.core.validators import (FileExtensionValidator)
from django.contrib.sites.models import Site
from uuid import uuid4
import uuid

# Create your models here.

class Sertificate(models.Model):
    """Сертификат"""
    name = models.CharField("Название", max_length=250)
    price = models.CharField("Цена", max_length=250)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Сертификат"
        verbose_name_plural = "Сертификаты"

class Templates(models.Model):
    """Шаблоны"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Название", max_length=250)
    description = models.TextField("Описание", db_index=True)
    price = models.CharField("Цена", max_length=250)
    cover = models.CharField("Обложка", max_length=250)
    system_name = models.CharField("Системное название", max_length=250, unique=True)
    json_file = models.FileField("Файл", upload_to='templates/%Y/%m/%d/')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Шаблоны"
        verbose_name_plural = "Шаблоны"



class Companys(models.Model):
    """Настройки сайта"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Название', max_length=500, blank=False)
    site = models.ManyToManyField(Site, verbose_name="Сайты", blank=True, null=True)
    logo = models.FileField("Логотип",  upload_to='settings/%Y/%m/%d/', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    doplogo = models.FileField("Дополнительный логотип",  upload_to='settings/%Y/%m/%d/', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    favicon = models.FileField("Фавикон", upload_to='settings/%Y/%m/%d/', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"


class TicketDeveloper(models.Model):
    date = models.DateTimeField(verbose_name="Дата", auto_now_add=True)
    STATUS_CHOICES = [
        (0, 'Новое'),
        (1, 'Обратная связь'),
        (2, 'В процессе'),
        (3, 'Решенный'),
        (4, 'Закрытый'),

    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.SmallIntegerField(verbose_name="Статус", choices=STATUS_CHOICES, default=0)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Автор",on_delete=models.CASCADE)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="ticket_developers_manager", verbose_name="Менеджер",on_delete=models.CASCADE)
    themas = models.TextField("Тема")
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Сайты", blank=True, null=True)

    class Meta:
        verbose_name = "Тикет разраба"
        verbose_name_plural = "Тикеты разраба"
        ordering = ['date']


class TicketDeveloperComment(models.Model):
    STATUS_CHOICES = [
        (0, 'Заказчик'),
        (1, 'Поддержка'),
    ]
    status = models.SmallIntegerField(verbose_name="Статус", choices=STATUS_CHOICES, default=1,  editable=False)
    ticket = models.ForeignKey(TicketDeveloper, on_delete=models.CASCADE, verbose_name="Ticket", related_name='ticket_developers_comments')
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    content = models.TextField(verbose_name="Комментарий")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Автор", blank=True, null=True)

    class Meta:
        verbose_name = "Комментарий тикета"
        verbose_name_plural = "Комментарии тикета"
        ordering = ['-date']


class TicketDeveloperCommentMedia(models.Model):
    comment = models.ForeignKey('TicketDeveloperComment', on_delete=models.CASCADE, related_name='ticket_developers_media')
    file = models.FileField(upload_to='ticket/%Y/%m/%d/tiket_file/')

    def get_file_name(self):
        return os.path.basename(self.file.name)

    class Meta:
        verbose_name = "Файл комментария тикета"
        verbose_name_plural = "Файлы комментариев тикета"