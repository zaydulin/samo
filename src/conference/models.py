from useraccount.models import Profile
from django.contrib.sites.models import Site

from django.db import models
from django.utils import timezone
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.conf import settings
from random import randrange, random
from django.db.models.signals import post_save
from django.dispatch import receiver
import random  # Импорт модуля random
import string  # Импорт модуля string
from datetime import timedelta

"""
Комната:
Сделать генерацию slug и token
"""

class VideoChatUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь", related_name='user_room', blank=True, null=True)
    hand = models.BooleanField(default=False)
    desktop = models.BooleanField(default=False)
    sound = models.BooleanField(default=True)
    video = models.BooleanField(default=True)
    sound_root = models.BooleanField(default=False)
    video_root = models.BooleanField(default=False)
    banned = models.BooleanField(default=False)
    saved_video = models.BooleanField(default=False)
    key = models.CharField(max_length=160, unique=True, verbose_name='ключ')
    name = models.CharField(max_length=160,  verbose_name='Имя', blank=True)
    dialog = models.FileField("svt-ФАЙЛ текст", upload_to='root/', null=True, blank=True)
    video = models.FileField("Видео", upload_to='root/', null=True, blank=True)
    offer = models.TextField()
    answer = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        # Проверка флагов sound_root и video_root перед сохранением
        if self.sound_root:
            self.sound = True
        if self.video_root:
            self.video = True
            self.desktop = True

        # Генерация уникального ключа, если он не установлен
        if not self.key:
            self.key = self._generate_unique_key()

        super().save(*args, **kwargs)

    def _generate_unique_key(self):
        max_tries = getattr(settings, 'RANDOM_PLAYLIST_URL_MAX_TRIES', 10)
        key_length = getattr(settings, 'RANDOM_PLAYLIST_URL_LENGTH', 8)  # Длина ключа
        charset = getattr(settings, 'RANDOM_PLAYLIST_URL_CHARSET', string.ascii_letters + string.digits)

        for _ in range(max_tries):
            new_key = "".join(random.choices(charset, k=key_length))
            if not VideoChatUser.objects.filter(key=new_key).exists():
                return new_key

        raise ValueError("Couldn't generate a unique key after multiple attempts.")
    class Meta:
        verbose_name = 'Пользователь для конференции'
        verbose_name_plural = 'Пользователи для конференции'

# Сигнал, создающий VideoChatUser при создании нового Profile
@receiver(post_save, sender=Profile)
def create_video_chat_user(sender, instance, created, **kwargs):
    if created:
        # Генерация ключа (или можно использовать другой способ генерации уникального ключа)
        random_key = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        VideoChatUser.objects.create(
            user=instance,
            key=random_key,
        )

@receiver(post_save, sender=Profile)
def save_video_chat_user(sender, instance, **kwargs):
    if hasattr(instance, 'video_chat_user'):
        instance.video_chat_user.save()

class VideoChatRoom(models.Model):
    TYPE = [
        (1, 'Общедоступная'),
        (2, 'Доступна только по ключу'),
    ]
    spiker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Ответственный", related_name='spiker',  blank=True)
    participants = models.ManyToManyField(VideoChatUser, verbose_name="Участники", related_name='participants',  blank=True)
    primary = models.ManyToManyField(VideoChatUser, verbose_name="Основной экран", related_name='primary', blank=True)
    visitors = models.ManyToManyField(VideoChatUser, verbose_name="Посетители", related_name='visitors', blank=True)
    notadded = models.ManyToManyField(VideoChatUser, verbose_name="не добавленные", related_name='notadded', blank=True)
    type = models.PositiveSmallIntegerField('Тип', choices=TYPE, blank=False, default=1)
    slug = models.SlugField(max_length=160, unique=True, verbose_name='Ссылка')
    course = models.ForeignKey('lms.Course', on_delete=models.CASCADE, verbose_name="Курс", blank=True, null=True)
    token = models.CharField(max_length=160, unique=True, verbose_name='Токен')
    descriptions = models.TextField(verbose_name='Описание', null=True, blank=True)
    logo = models.ImageField("Логотип", upload_to='root/', default='default/nophoto.png')
    cover = models.ImageField("Обложка", upload_to='root/', default='default/nophoto.png')
    banner = models.ImageField("Банер", upload_to='root/', default='default/nophoto.png')
    name = models.CharField(max_length=200, verbose_name='Название комнаты', null=True, blank=True)
    create = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    start_data = models.DateField( null=True, blank=True, verbose_name="Дата начало конференции")
    start_time = models.TimeField( null=True, blank=True, verbose_name="Время начало конференции")
    time = models.CharField( null=True, blank=True, max_length=200, verbose_name="Длительность")
    end_data = models.DateField( null=True, blank=True, verbose_name="Дата конца конференции")
    end_time = models.TimeField( null=True, blank=True, verbose_name="Время конца конференции")
    is_closed = models.BooleanField(default=True)
    is_start = models.BooleanField(default=False)
    high_resolution = models.BooleanField(default=False)
    count_participants_allowed = models.PositiveSmallIntegerField('Количество разрешенных участников', blank=False, default=0)
    count_participants_online = models.PositiveSmallIntegerField('Количество разрешенных онлайн', blank=False, default=0)
    count_participants = models.PositiveSmallIntegerField('Количество разрешенных онлайн', blank=False, default=0)
    dialog = models.FileField("svt-ФАЙЛ текст", upload_to='root/', default='default/nophoto.png', null=True, blank=True)
    signal_type = models.CharField(max_length=50)
    sdp = models.TextField(null=True, blank=True)
    candidate = models.TextField(null=True, blank=True)
    def save(self, *args, **kwargs):
        # Генерация уникального slug, если его нет
        if not self.slug:
            self.slug = self._generate_unique_slug()

        # Генерация уникального token, если его нет
        if not self.token:
            self.token = self._generate_unique_token()

        # Установка времени завершения на основе продолжительности
        if self.start_time and self.start_data and self.time:
            try:
                # Преобразуем длительность в минуты в timedelta
                duration_in_minutes = int(self.time)
                duration = timedelta(minutes=duration_in_minutes)
                # Определяем начальное время и дату
                start_datetime = timezone.datetime.combine(self.start_data, self.start_time)
                # Рассчитываем время окончания
                end_datetime = start_datetime + duration
                # Устанавливаем дату и время окончания
                self.end_data = end_datetime.date()
                self.end_time = end_datetime.time()
            except ValueError:
                raise ValueError("Поле 'time' должно содержать целое число, представляющее длительность в минутах.")

        # Вызов оригинального `save()` для сохранения изменений
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        loop_num = 0
        unique = False
        while not unique:
            if loop_num < settings.RANDOM_PLAYLIST_URL_MAX_TRIES:
                new_slug = self._generate_random_string(
                    settings.RANDOM_PLAYLIST_URL_LENGTH,
                    settings.RANDOM_PLAYLIST_URL_CHARSET,
                )
                if not VideoChatRoom.objects.filter(slug=new_slug).exists():
                    return new_slug
                loop_num += 1
            else:
                raise ValueError("Couldn't generate a unique slug.")

    def _generate_unique_token(self):
        loop_num = 0
        unique = False
        while not unique:
            if loop_num < settings.RANDOM_PLAYLIST_URL_MAX_TRIES:
                new_token = self._generate_random_string(
                    settings.RANDOM_PLAYLIST_URL_LENGTH,
                    settings.RANDOM_PLAYLIST_URL_CHARSET,
                )
                if not VideoChatRoom.objects.filter(token=new_token).exists():
                    return new_token
                loop_num += 1
            else:
                raise ValueError("Couldn't generate a unique token.")

    def _generate_random_string(self, length, charset):
        random_str = "".join(
            charset[randrange(0, len(charset))]
            for _ in range(length)
        )
        return random_str


    def get_absolute_url(self):
        return reverse('useraccount:video_chat_root', kwargs={"slug": self.slug})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Конференция'
        verbose_name_plural = 'Конференции'

class Signal(models.Model):
    room = models.ForeignKey(VideoChatRoom, on_delete=models.CASCADE, related_name='signals')
    user = models.ForeignKey(VideoChatUser, on_delete=models.CASCADE, related_name='signals')
    signal_type = models.CharField(max_length=50)
    sdp = models.TextField(null=True, blank=True)
    candidate = models.TextField(null=True, blank=True)

class VideoChatMessages(models.Model):
    """ Сообщения """
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='send_messages', verbose_name='Пользователь')
    videoroom = models.ForeignKey(VideoChatRoom, on_delete=models.CASCADE, related_name='videoroom_messages', verbose_name='Видеочат')
    content = models.TextField(verbose_name='Сообщения')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')

    def __str__(self):
        return f"{self.author} - {self.videoroom}"

    class Meta:
        verbose_name = 'Сообщение в конференции'
        verbose_name_plural = 'Сообщения в конференции'

class VideoChatFile(models.Model):
    """ Сообщения """
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='send_files', verbose_name='Пользователь')
    videoroom = models.ForeignKey(VideoChatRoom, on_delete=models.CASCADE, related_name='videoroom_files', verbose_name='Видеочат')
    file = models.FileField("svt-ФАЙЛ текст", upload_to='root/', default='default/nophoto.png')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')

    def __str__(self):
        return f"{self.author} - {self.videoroom}"

    class Meta:
        verbose_name = 'Файл в конференции'
        verbose_name_plural = 'Файл в конференции'