from django.db import models
from django.conf import settings
import os
import uuid
from django.contrib.sites.models import Site
from multiselectfield import MultiSelectField

class ModerationGroups(models.Model):
    """Группы"""
    TYPE_OPTION = [
        (1, 'Общяя'),
        (2, 'Внутреняя'),
    ]
    type_option = models.PositiveSmallIntegerField('Тип', choices=TYPE_OPTION, blank=False, default=1)
    TYPE_OPTIONS = (
        (1, 'Пользователи'),
        (2, 'Добавление пользователя'),
        (3, 'Удаления пользователя'),
        (4, 'Редактирование пользователя'),
        (5, 'Блокирование пользователя'),
        (6, 'Разблокировка пользователя'),
        (7, 'Группы'),
        (8, 'Добавление групп'),
        (9, 'Удаления/Редактирование групп'),
        (10, 'Добавление должностей'),
        (11, 'Заявки на рассмотрение'),
        (12, 'Обработка заявки на рассмотрение'),
        (13, 'Заявки на обратную связь'),
        (14, 'Обработка заявки на обратную связь'),
        (15, 'Задачи'),
        (16, 'Добавление задачи'),
        (17, 'Удаление задачи'),
        (18, 'Редактирование задачи'),
        (19, 'Записи'),
        (20, 'Добавление записи'),
        (21, 'Удаление записи'),
        (22, 'Редактирование паспортных данных в задаче'),
        (23, 'Добавление подзадачи'),
        (24, 'Удаление подзадачи'),
        (25, 'Редактирование подзадачи'),
        (26, 'Общие настройки сайта'),
        (27, 'Страницы'),
        (28, 'Добавление страницы'),
        (29, 'Удаление страницы'),
        (30, 'Редактирование страницы'),
        (31, 'Новости'),
        (32, 'Добавление новости'),
        (33, 'Удаление новости'),
        (34, 'Редактирование новости'),
        (35, 'ЧаВо'),
        (36, 'Добавление ЧаВо'),
        (37, 'Удаление ЧаВо'),
        (38, 'Редактирование ЧаВо'),
        (39, 'Галерея'),
        (40, 'Добавление галереи'),
        (41, 'Удаление галереи'),
        (42, 'Редактирование галереи'),
        (43, 'Тарифы'),
        (44, 'Добавление тарифа'),
        (45, 'Удаление тарифа'),
        (46, 'Редактирование тарифа'),
        (47, 'СЕО'),
        (48, 'Добавление СЕО'),
        (49, 'Удаление СЕО'),
        (50, 'Редактирование СЕО'),
        (51, 'Товары'),
        (52, 'Импорт'),
        (53, 'Склады'),
        (54, 'Добавление складов'),
        (55, 'Удаление складов'),
        (56, 'Редактирование складов'),
        (57, 'Контакты'),
        (58, 'Добавление контактов'),
        (59, 'Удаление контактов'),
        (60, 'Редактирование контактов'),
        (61, 'Бухгалтерия'),
        (62, 'Языки'),
        (63, 'Инструкция'),
        (64, 'Профиль'),
        (65, 'Проделанная работа'),
        (66, 'Личный график'),
        (67, 'Звонки'),
        (68, 'Мессенджеры'),
    )
    types = MultiSelectField(choices=TYPE_OPTIONS, blank=True, verbose_name='Доступ', default=[], max_length=255)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.TextField(editable=False)
    name = models.CharField(max_length=150, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='Пользователи', blank=True, related_name='groupusermoderation')

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


# Create your models here.
class Applications(models.Model):
    """Заявка """
    TYPE = [
        (1, 'Заявка'),
        (2, 'Покупка'),
    ]
    type = models.PositiveSmallIntegerField('Тип', choices=TYPE,  blank=True,null=True, default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Пользователь')
    email = models.CharField(blank=True, verbose_name='Email', max_length=500, null=True)
    phone = models.CharField(blank=True, verbose_name='Телефон', max_length=500, null=True)
    content = models.TextField(blank=True, null=True, verbose_name='Описание')
    create = models.DateTimeField(auto_now=True, blank=True,null=True)
    company_name = models.CharField(blank=True, verbose_name='Название компании', max_length=500, null=True)
    company_inn = models.CharField(blank=True, verbose_name='ИНН организации или ИП', max_length=500, null=True)
    company_director = models.CharField(blank=True, verbose_name='ФИО директора', max_length=500, null=True)
    company_adress = models.CharField(blank=True, verbose_name='Адрес', max_length=500, null=True)
    company_sku = models.CharField(blank=True, verbose_name='Количество товаров SKU в вашем каталоге', max_length=500, null=True)
    company_description = models.TextField(blank=True, null=True, verbose_name='Описание')

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"


class Ticket(models.Model):
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
    manager = models.ForeignKey(settings.AUTH_USER_MODEL,blank=True, null=True, related_name="ticket_manager", verbose_name="Менеджер",on_delete=models.CASCADE)
    themas = models.TextField("Тема")
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Сайты", blank=True, null=True)

    class Meta:
        verbose_name = "Тикет"
        verbose_name_plural = "Тикеты"
        ordering = ['date']


class TicketComment(models.Model):
    STATUS_CHOICES = [
        (0, 'Заказчик'),
        (1, 'Поддержка'),
    ]
    status = models.SmallIntegerField(verbose_name="Статус", choices=STATUS_CHOICES, default=1,  editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, verbose_name="Ticket", related_name='comments')
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    content = models.TextField(verbose_name="Комментарий")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Автор", blank=True, null=True)

    class Meta:
        verbose_name = "Комментарий тикета"
        verbose_name_plural = "Комментарии тикета"
        ordering = ['-date']


class TicketCommentMedia(models.Model):
    comment = models.ForeignKey('TicketComment', on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='ticket/%Y/%m/%d/tiket_file/')

    def get_file_name(self):
        return os.path.basename(self.file.name)

    class Meta:
        verbose_name = "Файл комментария тикета"
        verbose_name_plural = "Файлы комментариев тикета"


class DocumentationsModer(models.Model):
    name = models.CharField(blank=True, verbose_name='Название', max_length=500, null=True)
    description = models.TextField("Описание")
    TYPE_CHOICES = [
        (0, 'Для модераторов'),
        (1, 'Для пользователей'),
        (2, 'Для преподавателей'),
    ]
    type = models.SmallIntegerField(verbose_name="Тип", choices=TYPE_CHOICES, default=1)
    class Meta:
        verbose_name = "Документация"
        verbose_name_plural = "Документации"

    def __str__(self):
        return self.name

class DocumentationsModerMedia(models.Model):
    documentations = models.ForeignKey('DocumentationsModer', on_delete=models.CASCADE, related_name='documentations')
    file = models.FileField(upload_to='documentations/%Y/%m/%d/')

    def get_file_name(self):
        return os.path.basename(self.file.name)

    class Meta:
        verbose_name = "Файл документации"
        verbose_name_plural = "Файлы документации"

