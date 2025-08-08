from django.db import models
from ckeditor.fields import RichTextField
from django.urls import reverse
from django.conf import settings
from django.core.validators import (FileExtensionValidator)
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
import os
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid
import string
import random

from django.utils import timezone
from django.utils.text import slugify


# Create your models here.



class Courseuser(models.Model):
    """Прохождение курса"""
    STATUS_CHOICES = [
        (1, 'Оплата не прошла'),
        (2, 'Оплачено'),
    ]
    status = models.PositiveSmallIntegerField('Статус', choices=STATUS_CHOICES, blank=False, default=1)
    TYPE_CHOICES = [
        (1, 'Проходит'),
        (2, 'Пройден'),
    ]
    type = models.PositiveSmallIntegerField('Тип', choices=TYPE_CHOICES, blank=False, default=1)
    create = models.DateTimeField(auto_now=True, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь', on_delete=models.CASCADE, blank=True, null=True)
    question = models.ManyToManyField('Question', verbose_name="Варианты", blank=True)
    course = models.ForeignKey('Course', verbose_name='Курсы', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = "Прохождение курса"
        verbose_name_plural = "Прохождение курсов"


class Coursesertificateuser(models.Model):
    """Полученый сертификат курса"""
    create = models.DateTimeField(auto_now=True, blank=True, null=True)
    course = models.ForeignKey('Coursesertificate', verbose_name='Сертификат курса', on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь', on_delete=models.CASCADE, blank=True, null=True)
    certificate = models.FileField(upload_to='certificates/%Y/%m/%d/', blank=True, null=True, verbose_name="Сертификат", validators=[FileExtensionValidator(allowed_extensions=['pdf', 'png', 'jpg', 'webp'])])

    class Meta:
        verbose_name = "Полученый сертификат курса"
        verbose_name_plural = "Полученые сертификаты курсов"



class Courserewievs(models.Model):
    """Отзывы"""
    create = models.DateTimeField(auto_now=True, blank=True, null=True)
    course = models.ForeignKey('Course', verbose_name='Курс', on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь', on_delete=models.CASCADE, blank=True, null=True)
    estimate = models.PositiveIntegerField("Оценка")
    content = models.TextField(blank=True, null=True, verbose_name='Коментарий')

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"


class Coursecomments(models.Model):
    """Коментарии"""
    create = models.DateTimeField(auto_now=True, blank=True, null=True)
    course = models.ForeignKey('Course', verbose_name='Курс', on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь', on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField(blank=True, null=True, verbose_name='Коментарий')
    parent = models.ForeignKey('self', related_name='commentcourse', on_delete=models.CASCADE, blank=True, null=True, verbose_name='Родитель')

    class Meta:
        verbose_name = "Коментарий"
        verbose_name_plural = "Коментарий"



class Schedulestream(models.Model):
    created_at = models.DateTimeField('Дата создание', auto_now_add=True)
    data = models.DateField('Дата', blank=True, null=True)
    time_start = models.TimeField('Время начало', blank=True, null=True)
    time_end = models.TimeField('Время конца', blank=True, null=True)
    themes = models.ForeignKey('Themes', verbose_name='Тема', on_delete=models.CASCADE, blank=True, null=True, related_name='schedulestreamsthemes')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='Пользователи', blank=True, null=True)
    link = models.CharField(max_length=255, verbose_name='Ссылка', blank=True, null=True)
    logo = models.FileField(upload_to='settings/%Y/%m/%d/', blank=True, null=True, verbose_name="Лого", validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    cover = models.FileField(upload_to='settings/%Y/%m/%d/', blank=True, null=True, verbose_name="Обложка", validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)

    class Meta:
        verbose_name = 'График трансляций'
        verbose_name_plural = 'Графики трансляций'


class Coursesertificate(models.Model):
    """Сертификат курса"""
    description = models.TextField("Описание")
    previev = models.FileField(upload_to='certificate/%Y/%m/%d/', blank=True, null=True, verbose_name="Превью", default='default/certificate/defaultcert.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    create = models.DateTimeField(auto_now=True, blank=True, null=True)
    course = models.ForeignKey('Course', verbose_name='Курс', on_delete=models.CASCADE, blank=True, null=True)
    published = models.BooleanField(default=False)
    height = models.PositiveIntegerField(default=0, verbose_name='Высота')
    width = models.PositiveIntegerField(default=0, verbose_name='Ширина')

    def __str__(self):
        # Проверяем, есть ли у курса атрибут name или title
        return self.course.name if hasattr(self.course, 'name') else str(self.course)

    class Meta:
        verbose_name = "Сертификат курса"
        verbose_name_plural = "Сертификаты курсов"


class CategorysCourse(models.Model):
    """Категории"""
    created_at = models.DateTimeField('Дата создание', auto_now_add=True)
    name = models.CharField(max_length=150, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name='URL')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    title = models.CharField(max_length=150, verbose_name='Название',  null=True, blank=True)
    content = models.TextField(blank=True, null=True, verbose_name='Мета-описание')
    parent = models.ForeignKey('self', related_name='categorycourse', on_delete=models.CASCADE, blank=True, null=True, verbose_name='Родитель')
    cover = models.FileField("Обложка категории",   upload_to="category/%Y/%m/%d/", blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    icon = models.FileField("Иконка категории",   upload_to="category/%Y/%m/%d/", blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    image = models.FileField("Картинка категории",   upload_to="category/%Y/%m/%d/", blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('subCategorysCourse', kwargs={"slug": self.slug})

    def parent_name(self):
        return self.parent.name if self.parent else 'Нет родителя'

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Course(models.Model):
    """Курс"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Авторы', on_delete=models.CASCADE, blank=True, null=True)
    assistants = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='Помощники', related_name="assistants", blank=True, null=True)
    slug = models.SlugField(max_length=140, unique=True)
    name = models.CharField("Название", max_length=250)
    description = RichTextField("Описание")
    cover = models.FileField("Обложка",   upload_to="blogs/%Y/%m/%d/", blank=True, null=True, default="default/courseimage/1.png", validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    image = models.FileField("Изображение", default="default/courseimage/1.png" ,   upload_to="blogs/%Y/%m/%d/", blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    category = models.ManyToManyField(CategorysCourse, verbose_name="Категория", blank=True)
    previev = models.FileField(upload_to='settings/%Y/%m/%d/', blank=True, null=True, verbose_name="Превью", default='default/imagegallery/imagegellery_images.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    title = models.CharField(max_length=150, blank=True, null=True, verbose_name='Название')
    content = models.TextField(blank=True, null=True, verbose_name='Мета-описание')
    propertytitle = models.CharField(verbose_name="Мета-заголовок ссылки", max_length=150, blank=True, null=True,)
    propertydescription = models.CharField(verbose_name="Мета-описание ссылки", max_length=255, blank=True, null=True,)
    draft = models.BooleanField("Черновик", default=False)
    create = models.DateTimeField(auto_now=True, blank=True, null=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Сайт", default=1)
    price = models.PositiveIntegerField("Стоимость", default=0)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='Участники', related_name="participants", blank=True, null=True)
    TYPE = [
        (1, 'Доступно всем'),
        (2, 'Только выбранным'),
        (3, 'Закрыто для всех'),
    ]
    type = models.PositiveSmallIntegerField('Тип', choices=TYPE, blank=True, null=True, default=2)
    pageviews = models.PositiveIntegerField(verbose_name="Количество Просмотров",default=0, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)

    def generate_unique_slug(self):
        chars = string.ascii_lowercase + string.digits
        while True:
            slug = ''.join(random.choice(chars) for _ in range(20))
            if not Course.objects.filter(slug=slug).exists():
                return slug

    def get_absolute_url(self):
        return reverse('moderation:course', kwargs={"slug": self.slug})

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class CourseSettings(models.Model):
    course = models.ForeignKey(Course, verbose_name='Курсы', on_delete=models.CASCADE, blank=True, null=True)
    data_start = models.DateField(verbose_name='С даты', null=True, blank=True)
    data_end = models.DateField(verbose_name='По дату', null=True, blank=True)

    class Meta:
        verbose_name = "Настройка"
        verbose_name_plural = "Настройки"

class Modules(models.Model):
    course = models.ForeignKey(Course, verbose_name='Курсы', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField("Название", max_length=250)
    position = models.PositiveIntegerField('Позиция', null=True, blank=True)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Модуль"
        verbose_name_plural = "Модули"

class CourseAssistents(models.Model):
    course = models.ForeignKey(Course, verbose_name='Курсы', related_name='assistentscourse', on_delete=models.CASCADE, blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Авторы', on_delete=models.CASCADE, blank=True, null=True)
    bookmark_as = models.BooleanField("Добавялть в свою библиотеку", default=False)

    class Meta:
        verbose_name = "Ассистент"
        verbose_name_plural = "Ассистенты"



class Themes(models.Model):
    course = models.ForeignKey(Course, verbose_name='Курсы', related_name='themescourse', on_delete=models.CASCADE, blank=True, null=True)
    modules = models.ForeignKey(Modules, verbose_name='Модули', related_name='modulescourse', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField("Название", max_length=250)
    description = models.TextField("Описание")
    position = models.PositiveIntegerField('Позиция', null=True, blank=True)
    point = models.PositiveIntegerField('Баллов для прохождения', null=True, blank=True)
    point_status = models.BooleanField("Начислять баллы", default=False)
    attempts = models.PositiveIntegerField('Попытки за прохождения в минуты', null=True, blank=False)
    attempts_status = models.BooleanField("Ограничить попытки прохождениея", default=False)
    test_duration = models.PositiveIntegerField("Время на тест", null=True, blank=True)  # Поле для времени теста
    access_type = models.BooleanField("Доступна после прохождения предыдущего", default=False)
    show_answer = models.BooleanField("После прохождения показывать ответы", default=False)
    home_work = models.TextField("Домашнее задание", null=True, blank=True)
    home_work_status = models.BooleanField("Наличие домашнего задания", default=False)


    def __str__(self):
        return self.name

    class Meta:
        ordering = ['position']
        verbose_name = "Тема"
        verbose_name_plural = "Темы"

class Files(models.Model):
    TYPE = [
        (1, 'Видео'),
        (2, 'Аудио'),
        (3, 'Документ'),
    ]
    type = models.PositiveSmallIntegerField('Тип', choices=TYPE, blank=True, null=True, default=2)
    name = models.CharField("Название", blank=True, null=True, max_length=250)
    theme = models.ForeignKey('Themes', on_delete=models.CASCADE, related_name='themes_file')
    files = models.FileField(upload_to='coursemedia/%Y/%m/%d/', blank=True, null=True, verbose_name="Файл")
    content = models.TextField(blank=True, null=True, verbose_name='Вставка')
    link = models.BooleanField("Загрузить на хостинг", default=False)
    create = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"

    def save(self, *args, **kwargs):
        # Automatically set the name if it's empty or null
        if self.files and (not self.name or self.name.strip() == ""):
            # Extract the file name without the extension
            self.name = os.path.splitext(self.files.name)[0]
        super(Files, self).save(*args, **kwargs)

class StreamSession(models.Model):
    theme = models.ForeignKey(Themes, on_delete=models.CASCADE, related_name='stream_sessions')
    date = models.DateField('Дата')
    time = models.PositiveIntegerField('Длительность', blank=True, null=True)
    time_start = models.TimeField('Время начала')
    time_end = models.TimeField('Время окончания')


    def __str__(self):
        return f"Stream for {self.theme.name} on {self.date}"

    class Meta:
        verbose_name = "Сессия трансляции"
        verbose_name_plural = "Сессии трансляций"


class ThemesQuestion(models.Model):
    STATUS = [
        (1, 'Прошел'),
        (2, 'Проходит'),
        (3, 'Не сдал'),
    ]
    status = models.PositiveSmallIntegerField('Статус', choices=STATUS, blank=True, null=True, default=2)
    themes = models.ForeignKey(Themes, on_delete=models.CASCADE, related_name='themes_questions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    qwiz = models.TextField(max_length=900, blank=True, null=True)
    data = models.DateTimeField(blank=True, null=True)
    point = models.PositiveIntegerField(blank=True, null=True)
    correctanswer = models.PositiveIntegerField(blank=True, null=True,default=0)
    last_attempt_time = models.DateTimeField(default=timezone.now) # Время оставшееся в секундах

    def __str__(self):
        return f"Контроль для темы {self.themes.name} для пользователя {self.user} {self.get_status_display()}"

    class Meta:
        verbose_name = "Контроль прохождения"
        verbose_name_plural = "Контроли прохождения"

class Qwiz(models.Model):
    """Задания"""
    TYPE = [
        (1, 'Домашнее задания'),
        (2, 'Тесты'),
        (3, 'Тесты с картинками'),
        (4, 'Выборка'),
        (5, 'Заполните пропуск'),
        (6, 'Выберите соответствие'),
    ]
    type = models.PositiveSmallIntegerField('Тип', choices=TYPE,  blank=True,null=True, default=1)
    themes = models.ForeignKey(Themes, verbose_name='Тема', on_delete=models.CASCADE, blank=True, related_name='quizzes', null=True)
    name = models.CharField("Название", max_length=250)
    description = models.TextField("Описание")
    position = models.PositiveIntegerField('Позиция', null=True, blank=True)
    point = models.PositiveIntegerField(blank=True, null=True, default=0)

    def __str__(self):
        return self.name

    def get_count_of_correct_answers(self):
        questions = self.question_quiz.all()
        correct_answers_count = questions.filter(right_answer=2).count()
        return correct_answers_count


    class Meta:
        verbose_name = "Задание"
        verbose_name_plural = "Задания"


class Question(models.Model):
    """Вопрос"""
    STATUS = [
        (1, 'Не правильный'),
        (2, 'Правильный'),
    ]
    right_answer = models.PositiveSmallIntegerField('Правильный ответ', choices=STATUS,  blank=True,null=True, default=1)
    qwiz = models.ForeignKey(Qwiz, verbose_name='Задания', on_delete=models.CASCADE, blank=True, null=True, related_name="question_quiz")
    title = models.CharField("Заголовок", max_length=250)
    second_title = models.CharField("Заголовок 2", max_length=250, blank=True, null=True)
    image = models.FileField("Изображение",   upload_to="blogs/%Y/%m/%d/", blank=True, null=True, default='default/blogs/cover.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    description = models.TextField("Текст")
    hints = models.ManyToManyField('HintsToQuestion', verbose_name="Подсказки к вопросу", blank=True)
    left_text = models.CharField("Левый текст для 6 теста", max_length=250, blank=True, null=True)
    right_text = models.CharField("Правый текст для 6 теста", max_length=250, blank=True, null=True)
    left_file = models.FileField("Левое Изображение 6 теста",   upload_to="blogs/%Y/%m/%d/", blank=True, null=True, default='default/blogs/cover.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    right_file = models.FileField("Правое Изображение 6 теста",   upload_to="blogs/%Y/%m/%d/", blank=True, null=True, default='default/blogs/cover.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)

    def __str__(self):
        return f'{self.title}-{self.qwiz}'


    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

class HintsToQuestion(models.Model):
    STATUS = [
        (1, 'Не правильный'),
        (2, 'Правильный'),
    ]
    name = models.CharField(max_length=250)
    right_answer = models.PositiveSmallIntegerField('Правильный ответ', choices=STATUS, blank=True, null=True,
                                                    default=1)
    def __str__(self):
        return self.name


    class Meta:
        verbose_name = "Подсказка"
        verbose_name_plural = "Подсказки"


class HomeWork(models.Model):
    text = RichTextField("Ответ пользователя")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, )
    theme = models.ForeignKey(Themes, on_delete=models.CASCADE, blank=True, null=True, related_name='homework')
    class Meta:
        verbose_name = "Домашнее задание"
        verbose_name_plural = "Домашние задания"

class HomeWorkFiles(models.Model):
    TYPE = [
        (1, 'Видео'),
        (2, 'Аудио'),
        (3, 'Документ'),
    ]
    type = models.PositiveSmallIntegerField('Тип', choices=TYPE, blank=True, null=True, default=3)
    name = models.CharField("Название", blank=True, null=True, max_length=250)
    homework = models.ForeignKey(
        'HomeWork',
        on_delete=models.CASCADE,
        related_name='homework_files',
        verbose_name="Домашнее задание"
    )
    file = models.FileField(upload_to='homework_files/%Y/%m/%d/', blank=True, null=True, verbose_name="Файл")
    content = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    link = models.BooleanField("Загрузить на хостинг", default=False)
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        verbose_name = "Файл домашнего задания"
        verbose_name_plural = "Файлы домашних заданий"

    def save(self, *args, **kwargs):
        # Если имя файла пустое, автоматически устанавливаем его из имени загружаемого файла
        if self.file and (not self.name or self.name.strip() == ""):
            self.name = os.path.splitext(self.file.name)[0]
        super().save(*args, **kwargs)

class Needcourse(models.Model):
    """Нужен курс"""
    TYPE_CHOICES = [
        (1, 'Опубликован'),
        (2, 'Закрыт'),
        (3, 'Найден исполнитель'),
    ]
    type = models.PositiveSmallIntegerField('Тип', choices=TYPE_CHOICES, blank=False, default=1)
    name = models.CharField("Название", max_length=250)
    description = RichTextField("Описание",db_index=True)
    slug = models.SlugField(max_length=140, unique=True)
    price = models.PositiveIntegerField("Стоимость")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('needcourse', kwargs={"slug": self.slug})


    class Meta:
        verbose_name = "Нужен курс"
        verbose_name_plural = "Нужен курс"


class Assumptioncourse(models.Model):
    """Предложение курс"""
    needcourse = models.ForeignKey('Needcourse', verbose_name='Нужен курс', on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    price = models.PositiveIntegerField("Стоимость")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = "Предположение курс"
        verbose_name_plural = "Предположение курс"