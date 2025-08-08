from ckeditor.fields import RichTextField
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import (FileExtensionValidator)
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
import uuid
import os
from uuid import uuid4
from django.contrib.sites.models import Site
from multiselectfield import MultiSelectField
from django.contrib.contenttypes.fields import GenericForeignKey


def get_user_dir(instance, filename) -> str:
    extension = filename.split(".")[-1]
    return f"users/user_{instance.id}.{extension}"

class Profile(AbstractUser):
    """Персона"""
    GENDER_CHOICE = [
        (1, 'Мужской'),
        (2, 'Женский'),
    ]
    TYPE = [
        (0, 'Ученик'),
        (1, 'Учитель'),
        (2, 'Модератор'),
    ]
    type = models.PositiveSmallIntegerField('Тип пользователя', choices=TYPE, blank=True, null=True, default=0)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(blank=True, verbose_name='Телефон', max_length=500, null=True, unique=True)
    email = models.EmailField('Email', unique=True)
    avatar = models.FileField(
        upload_to=get_user_dir, blank=True, null=True,
        verbose_name='Аватар',
        default='default/user-nophoto.png',
        validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])]
    )
    device_token = models.TextField(blank=True, null=True, verbose_name="FCM токен устройства")
    gender = models.PositiveSmallIntegerField('Пол', choices=GENDER_CHOICE, blank=True, null=True, default=1)
    birthday = models.DateField(verbose_name='Дата рождения', blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, verbose_name='Город', null=True)
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Отчество')
    online = models.BooleanField(default=False, verbose_name="Онлайн")
    blocked = models.BooleanField(default=False, verbose_name="Заблокирован")
    deleted = models.BooleanField(default=False, verbose_name="Удален")
    earned = models.PositiveSmallIntegerField(verbose_name='Заработано', blank=True, null=True, default=0)
    balance = models.PositiveSmallIntegerField(verbose_name='Баланс', blank=True, null=True, default=0)
    frozen = models.PositiveSmallIntegerField(verbose_name='Замороженный баланс', blank=True, null=True, default=0)
    """Реферальная система"""
    point = models.PositiveSmallIntegerField(verbose_name='Баллы', blank=True, null=True, default=0)
    referral = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='Пользователь', blank=True, null=True, on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=100, blank=True, null=True, verbose_name='Личный код')
    """Паспортные данные пользователя"""
    passport_issued_by_whom = models.TextField("Кем выдан", blank=True, null=True)
    passport_date_of_issue = models.DateField(verbose_name='Дата выдачи', blank=True, null=True)
    passport_the_sub_division_code = models.CharField(max_length=100, blank=True, null=True, verbose_name='Код подрозделения')
    passport_series_and_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='Серия и номер')
    passport_place_of_birth = models.TextField("Место рождения", blank=True, null=True)
    passport_registration = models.TextField("Прописка", blank=True, null=True)
    passport_image_1 = models.FileField(
        upload_to=get_user_dir, blank=True, null=True,
        verbose_name='Лицевая часть',
        default='default/user-nophoto.png',
        validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])]
    )
    passport_image_2 = models.FileField(
        upload_to=get_user_dir, blank=True, null=True,
        verbose_name='Место прописки',
        default='default/user-nophoto.png',
        validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])]
    )

    """Данные по организации"""
    company_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Название организации')
    company_director = models.CharField(max_length=100, blank=True, null=True, verbose_name='Руководитель')
    company_address = models.CharField(max_length=100, blank=True, null=True, verbose_name='Юридический адрес')
    company_nalogovaya = models.CharField(max_length=100, blank=True, null=True, verbose_name='Налоговый орган')
    company_ogrn = models.CharField(max_length=100, blank=True, null=True, verbose_name='ОГРН')
    company_inn = models.CharField(max_length=100, blank=True, null=True, verbose_name='ИНН')
    company_kpp = models.CharField(max_length=100, blank=True, null=True, verbose_name='КПП')
    company_data_registration = models.DateField(verbose_name='Дата регистрации', blank=True, null=True)
    company_type_activity = models.TextField("Основной вид деятельности", blank=True, null=True)


    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class History(models.Model):
    """История"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='Пользователь', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,limit_choices_to={'model__in': ('blogs','course',)})
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField('Время просмотра',auto_now_add=True)

    class Meta:
        verbose_name = "История"
        verbose_name_plural = "История"


class Notebook(models.Model):
    created_at = models.DateTimeField('Дата создание', auto_now_add=True)
    period = models.DateField('Периуд')
    name = models.CharField("Название", max_length=250)
    description = models.TextField("Описание", db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='Пользователь', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Личная запись'
        verbose_name_plural = 'Личные записи'


class Withdrawal(models.Model):
    """Выплаты"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='Пользователь', on_delete=models.CASCADE)
    amount = models.CharField("Сумма", max_length=250, blank=True, null=True)
    TYPE_CHOICES = [
        (0, 'Пополнение'),
        (1, 'Списание'),
    ]
    type = models.SmallIntegerField(verbose_name="Пополнение/Списание", choices=TYPE_CHOICES, default=0)
    STATUS_CHOICES = [
        (0, 'Поданна заявка'),
        (1, 'Выполнено'),
    ]
    status = models.SmallIntegerField(verbose_name="Статус", choices=STATUS_CHOICES, default=0)

    create = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Выплата"
        verbose_name_plural = "Выплаты"

class UserSessionBridge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    url = models.TextField(verbose_name="URL", blank=True, null=True)
    time = models.PositiveIntegerField(verbose_name="Время", blank=True, null=True)
    date = models.CharField(verbose_name="date", max_length=150)

    def __str__(self):
        return f'{self.user} - {self.url}'

    class Meta:
        verbose_name = "Тайминг модератора2"
        verbose_name_plural = "Тайминги модераторов2"

class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    info = models.TextField(verbose_name="Информация", blank=True, null=True)
    month = models.TextField(verbose_name='Месяц', blank=True, null=True)

    def __str__(self):
        return f'{self.info}'

    class Meta:
        verbose_name = "Тайминг модератора"
        verbose_name_plural = "Тайминги модераторов"


class Schedule(models.Model):
    created_at = models.DateTimeField('Дата создание', auto_now_add=True)
    data = models.DateField('Дата')
    time_start = models.TimeField('Время начало')
    time_end = models.TimeField('Время конца')
    name = models.CharField("Название", max_length=250)
    description = models.TextField("Описание", db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='Пользователь', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'График'
        verbose_name_plural = 'Графики'

class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     limit_choices_to={'model__in': ('blogs', 'course',)})
    object_id = models.UUIDField()  # Изменено с PositiveIntegerField
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        verbose_name = "Закладка"
        verbose_name_plural = "Закладки"


class Notificationgroups(models.Model):
    """Уведомление"""
    user = models.ManyToManyField(settings.AUTH_USER_MODEL,verbose_name='Пользователь')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    created_at = models.DateTimeField('Время отправки', auto_now_add=True)
    message = models.TextField()
    slug = models.TextField(editable=False)

    class Meta:
        verbose_name = "Груповое уведомление"
        verbose_name_plural = "Груповые уведомления"


class Notification(models.Model):
    """Уведомление"""
    TYPE = [
        (1, 'Регистрация'),
        (2, 'Покупка'),
        (3, 'Сбросить пароль'),
        (4, 'Рассылка'),
    ]
    type = models.PositiveSmallIntegerField('Тип', choices=TYPE, blank=False, default=1)
    STATUS = [
        (1, 'Не прочитан'),
        (2, 'Прочитан'),
    ]
    status = models.PositiveSmallIntegerField("Статус", choices=STATUS, blank=False, default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='Пользователь', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    created_at = models.DateTimeField('Время отправки',auto_now_add=True)
    message = models.TextField()
    content_object = GenericForeignKey('content_type', 'object_id')
    slug = models.TextField(editable=False)

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"



def chat_message_media_upload_to(instance, filename):
    # Получаем ID чата из связанного объекта ChatMessage
    chat_id = instance.comment.chat.id
    # Создаем уникальное имя файла, чтобы избежать конфликтов
    unique_filename = f"{uuid4()}_{filename}"
    # Возвращаем кастомный путь
    return os.path.join('chat', str(chat_id), unique_filename)

class Chat(models.Model):
    TYPE = [
        (1, 'Групповой'),
        (2, 'Личные'),
    ]
    type = models.PositiveSmallIntegerField('Тип', choices=TYPE, blank=False, default=1)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='Владелец',on_delete=models.CASCADE, related_name='chatowner')
    administrators = models.ManyToManyField(settings.AUTH_USER_MODEL,verbose_name='Администраторы', related_name='chatadministrators')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='Пользователи', related_name='chatusers')
    name = models.CharField(max_length=150, verbose_name='Название', blank=True, null=True)

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"

class ChatMessage(models.Model):
    STATUS_CHOICES = [
        (0, 'Отправлено'),
        (1, 'Прочитано'),
    ]
    status = models.SmallIntegerField(verbose_name="Статус", choices=STATUS_CHOICES, default=1,  editable=False)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, verbose_name="Чат", related_name='chatmessage')
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    content = models.TextField(verbose_name="Сообщение")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Автор", blank=True, null=True)
    views = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='Пользователи', related_name='viewsmessage')

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['-date']

class ChatMessageMedia(models.Model):
    comment = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='chatmessagemedia')
    file = models.FileField(upload_to='chat_message_media_upload_to/%Y/%m/%d/')
    filename = models.CharField("Имя", max_length=250, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.filename:
            self.filename = os.path.basename(self.file.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Файл сообщений чата"
        verbose_name_plural = "Файлы сообщений чата"