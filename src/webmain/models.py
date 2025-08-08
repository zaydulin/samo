from email.policy import default

from django.db import models
from ckeditor.fields import RichTextField
from django.urls import reverse
from django.conf import settings
from django.core.validators import (FileExtensionValidator)
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
import os
import uuid
from django_grapesjs.models import GrapesJsHtmlField






class Seo(models.Model):
    """Персона"""
    PAGE_CHOICE = [
        (1, 'Главная страница'),
        (2, 'Новости'),
        (3, 'Каталог'),
        (4, 'Поиск'),
        (5, 'Покупки'),
        (6, 'Профиль'),
        (7, 'Закладки'),
        (8, 'Ресгистрации'),
        (9, 'Авторизация'),
        (10, 'Сбросить пароль'),
        (11, 'Партнерство'),
        (12, 'Сотрудничество'),
        (13, 'Контакты'),
        (14, 'ЧаВО'),
        (15, 'Специалисты'),
        (16, 'Поставщик социальных услуг'),
    ]
    pagetype = models.PositiveSmallIntegerField('Странца', unique=True, choices=PAGE_CHOICE, blank=False, default=1)
    previev = models.FileField(upload_to='settings/%Y/%m/%d/', blank=True, null=True, verbose_name="Превью", default='default/imagegallery/imagegellery_images.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    title = models.CharField(verbose_name="Мета-заголовок", max_length=150, blank=True, null=True,)
    description = models.CharField(verbose_name="Мета-описание", max_length=255, blank=True, null=True,)
    propertytitle = models.CharField(verbose_name="Мета-заголовок ссылки", max_length=150, blank=True, null=True,)
    propertydescription = models.CharField(verbose_name="Мета-описание ссылки", max_length=255, blank=True, null=True,)
    setting = models.ForeignKey("SettingsGlobale", verbose_name='Настройки', on_delete=models.CASCADE, blank=True, null=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Сайты", blank=True, null=True)

    class Meta:
        verbose_name = "Сео страницы"
        verbose_name_plural = "Сео страниц"

class SettingsGlobale(models.Model):
    """Настройки сайта"""
    logo = models.FileField("Логотип",  upload_to='settings/%Y/%m/%d/', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    doplogo = models.FileField("Дополнительный логотип",  upload_to='settings/%Y/%m/%d/', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    favicon = models.FileField("Фавикон", upload_to='settings/%Y/%m/%d/', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    paymentmetod = models.FileField("Методы оплаты", upload_to='settings/%Y/%m/%d/', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    name = models.CharField("Название", max_length=500, blank=True, null=True)
    content = models.CharField("Копирайт", max_length=500, blank=True, null=True)
    description = RichTextField("Описание", blank=True, null=True)
    message_header = models.TextField("Шапка сообщения письма", blank=True, null=True)
    message_footer = models.TextField("Подвал сообщения письма", blank=True, null=True)
    yandex_metrica = models.TextField("Яндекс метрика", blank=True, null=True)
    google_analitic = models.TextField("Гугл аналитика", blank=True, null=True)
    specialists = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='Специалисты')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Сайты", blank=True, null=True)


    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Настройка сайта"
        verbose_name_plural = "Настройки сайта"

class ContactPage(models.Model):
    """Настройки сайта"""
    setting = models.ForeignKey(SettingsGlobale, verbose_name='Настройки', on_delete=models.CASCADE, blank=True,null=True)
    phone = models.CharField(verbose_name="Телефон", max_length=150, blank=True, null=True,)
    email = models.CharField(verbose_name="Эл.Почта", max_length=150, blank=True, null=True,)
    adress = models.CharField(verbose_name="Адресс", max_length=150, blank=True, null=True,)
    latitude = models.FloatField("Широта", blank=True, null=True)
    longitude = models.FloatField("Долгота", blank=True, null=True)
    telegram = models.CharField(verbose_name="Телеграм", max_length=150, blank=True, null=True)
    whatsapp = models.CharField(verbose_name="Вацап", max_length=150, blank=True, null=True)
    vk = models.CharField(verbose_name="ВКонтакте", max_length=150, blank=True, null=True)
    grafik = models.CharField(verbose_name="График", max_length=150, blank=True, null=True, )
    site = models.OneToOneField(Site, on_delete=models.CASCADE, verbose_name="Сайт", default=1)

    class Meta:
        verbose_name = "Страница контакты"
        verbose_name_plural = "Страницы контакты"

class Testimonial(models.Model):
    """Настройки сайта"""
    description = models.TextField(verbose_name="Комментарий", blank=True, null=True)
    name = models.CharField(verbose_name="Имя", max_length=150, blank=True, null=True)
    image = models.FileField(upload_to='settings/%Y/%m/%d/', blank=True, null=True, verbose_name="Изображение", default='default/imagegallery/imagegellery_images.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    site = models.OneToOneField(Site, on_delete=models.CASCADE, verbose_name="Сайт", default=1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

class Pages(models.Model):
    """Страницы"""
    PAGETYPE = [
        (1, 'Стандартная'),
        (2, 'Пользовательское соглашение'),
        (3, 'Политика конфедециальности'),
        (4, 'Политика Cookie - Файлов'),
        (5, 'Согласия на обработку персональных данных'),
        (6, 'Порядок предоставления услуг'),
    ]
    pagetype = models.PositiveSmallIntegerField('Тип', choices=PAGETYPE, blank=False, default=1)
    name = models.CharField("Название", max_length=250)
    description = RichTextField("Описание", db_index=True)
    title = models.CharField(max_length=150, blank=True, null=True, verbose_name='Заголовок')
    content = models.TextField(blank=True, null=True, verbose_name='Мета-описание')
    previev = models.FileField(
        upload_to='settings/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Превью",
        default='default/imagegallery/imagegellery_images.png',
        validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])]
    )
    propertytitle = models.CharField(verbose_name="Мета-заголовок ссылки", max_length=150, blank=True, null=True)
    propertydescription = models.CharField(verbose_name="Мета-описание ссылки", max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=140, unique=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Сайты", blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('pages', kwargs={"slug": self.slug})

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"


class Organizations(models.Model):
    """Страницы"""
    name = models.CharField("Название", max_length=250)
    description = RichTextField("Описание",db_index=True)
    icon = models.FileField(upload_to='settings/%Y/%m/%d/', blank=True, null=True, verbose_name="Иконка", default='default/imagegallery/imagegellery_images.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    longitude = models.CharField("Долгота", max_length=250)
    width = models.CharField("Широта", max_length=250)
    title = models.CharField(max_length=150, blank=True, null=True, verbose_name='Заголовок')
    content = models.TextField(blank=True, null=True, verbose_name='Мета-описание')
    previev = models.FileField(upload_to='settings/%Y/%m/%d/', blank=True, null=True, verbose_name="Превью", default='default/imagegallery/imagegellery_images.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    propertytitle = models.CharField(verbose_name="Мета-заголовок ссылки", max_length=150, blank=True, null=True,)
    propertydescription = models.CharField(verbose_name="Мета-описание ссылки", max_length=255, blank=True, null=True,)
    slug = models.SlugField(max_length=140, unique=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Сайты", blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('organizations', kwargs={"slug": self.slug})


    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"

class Jobs(models.Model):
    """Вакансии"""
    name = models.CharField("Название", max_length=250)
    location = models.CharField(max_length=100, verbose_name="Местоположение")
    description = models.TextField(verbose_name="Описание вакансии")
    requirements = models.TextField(verbose_name="Требования")
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Зарплата")
    job_type = models.CharField(max_length=20, choices=[
        ('full_time', 'Полная занятость'),
        ('part_time', 'Частичная занятость'),
        ('contract', 'Контракт'),
        ('internship', 'Стажировка'),
    ], verbose_name="Тип занятости")
    experience_level = models.CharField(max_length=20, choices=[
        ('entry', 'Начальный'),
        ('mid', 'Средний'),
        ('senior', 'Старший'),
        ('lead', 'Ведущий'),
    ], verbose_name="Уровень опыта")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    title = models.CharField(max_length=150, blank=True, null=True, verbose_name='Заголовок')
    content = models.TextField(blank=True, null=True, verbose_name='Мета-описание')
    previev = models.FileField(upload_to='settings/%Y/%m/%d/', blank=True, null=True, verbose_name="Превью", default='default/imagegallery/imagegellery_images.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    propertytitle = models.CharField(verbose_name="Мета-заголовок ссылки", max_length=150, blank=True, null=True,)
    propertydescription = models.CharField(verbose_name="Мета-описание ссылки", max_length=255, blank=True, null=True,)
    slug = models.SlugField(max_length=140, unique=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Сайты", blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('jobs', kwargs={"slug": self.slug})


    class Meta:
        verbose_name = "Вакансии"
        verbose_name_plural = "Вакансии"

class Faqs(models.Model):
    """Вопрос """
    question = models.TextField(blank=True, null=True, verbose_name='Вопрос')
    answer = models.TextField(blank=True, null=True, verbose_name='Ответ', default=' ')
    create = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    update = models.DateTimeField(auto_now=True, blank=True, null=True)
    publishet = models.BooleanField("Опубликован", default=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Сайт", default=1)


    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

class Categorys(models.Model):
    """Категории"""
    name = models.CharField(max_length=150, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name='URL')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    title = models.CharField(max_length=150, verbose_name='Название',  null=True, blank=True)
    content = models.TextField(blank=True, null=True, verbose_name='Мета-описание')
    parent = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, blank=True, null=True, verbose_name='Родитель')
    cover = models.FileField("Обложка категории",   upload_to="category/%Y/%m/%d/", blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    icon = models.FileField("Иконка категории",   upload_to="category/%Y/%m/%d/", blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    image = models.FileField("Картинка категории",   upload_to="category/%Y/%m/%d/", blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Сайт", default=1)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('subcategorys', kwargs={"slug": self.slug})

    def parent_name(self):
        return self.parent.name if self.parent else 'Нет родителя'

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class Blogs(models.Model):
    """Блог"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Авторы', on_delete=models.CASCADE, blank=True, null=True)
    resource = models.CharField("Источник", max_length=550, blank=True, null=True)
    category = models.ManyToManyField(Categorys, verbose_name="Категория", blank=True)
    name = models.CharField("Название", max_length=250)
    description = RichTextField("Описание",db_index=True)
    previev = models.FileField(upload_to='settings/%Y/%m/%d/', blank=True, null=True, verbose_name="Превью", default='default/imagegallery/imagegellery_images.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    title = models.CharField(max_length=150, unique=True, verbose_name='Название')
    content = models.TextField(blank=True, null=True, verbose_name='Мета-описание')
    propertytitle = models.CharField(verbose_name="Мета-заголовок ссылки", max_length=150, blank=True, null=True,)
    propertydescription = models.CharField(verbose_name="Мета-описание ссылки", max_length=255, blank=True, null=True,)
    slug = models.SlugField(max_length=140, unique=True)
    cover = models.FileField("Обложка",   upload_to="blogs/%Y/%m/%d/", blank=True, null=True, default='default/blogs/cover.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    draft = models.BooleanField("Черновик", default=False)
    create = models.DateTimeField(auto_now=True, blank=True, null=True)
    date_time = models.DateTimeField("Дата и время", blank=True, null=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Сайт", default=1)
    pageviews =  models.PositiveIntegerField(verbose_name="Количество Просмотров",default=0, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('webmain:blog', kwargs={"slug": self.slug})

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

class SettingsTemplate(models.Model):
    """Настройки сайта"""
    templates = models.CharField('Шаблон', max_length=500, blank=False, default='site')
    setting = models.ForeignKey(SettingsGlobale, verbose_name='Настройки', on_delete=models.CASCADE, blank=True, null=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Сайты", blank=True, null=True)
    multilingual_enabled = models.BooleanField(default=False, verbose_name="Включить мультиязычность")
    json_file = models.FileField(upload_to='templates_original/%Y/%m/%d/')

    class Meta:
        verbose_name = "Настройка шаблона"
        verbose_name_plural = "Настройки шаблонов"

    @classmethod
    def get_settings(cls):
        return cls.objects.first()


class DocumentationsSite(models.Model):
    name = models.CharField(blank=True, verbose_name='Название', max_length=500, null=True)
    description = models.TextField("Описание")
    file = models.FileField(upload_to='documentations/%Y/%m/%d/')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Сайты", blank=True, null=True, default=1)

    class Meta:
        verbose_name = "Документация"
        verbose_name_plural = "Документации"

    def __str__(self):
        return self.name


class Landing(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    html_content = models.TextField()
    css_content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

