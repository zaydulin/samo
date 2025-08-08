import base64
import os
import random
import re

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.timezone import now
from django.template import Template, Context
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import m2m_changed
from django.db import transaction
from xhtml2pdf import pisa
from html2image import Html2Image
from PIL import Image, ImageDraw, ImageFont
from useraccount.models import Notificationgroups, Notification, Profile
from django.contrib.contenttypes.models import ContentType
from lms.models import Coursesertificateuser, Coursesertificate

@receiver(m2m_changed, sender=Notificationgroups.user.through)
def create_notifications_on_user_added(sender, instance, action, pk_set, **kwargs):
    # Сработает, когда пользователи добавлены в группу
    if action == "post_add":
        content_type = ContentType.objects.get_for_model(instance)


        # Проверка наличия идентификаторов пользователей в pk_set
        if not pk_set:
            return

        # Используем атомарный блок для создания уведомлений
        with transaction.atomic():
            for user_id in pk_set:
                try:
                    # Получаем пользователя по ID
                    user = Profile.objects.get(id=user_id)

                    # Создаем уведомление для каждого пользователя
                    Notification.objects.create(
                        type=4,
                        status=1,
                        user=user,
                        content_type=content_type,
                        object_id=instance.id,  # Предполагается, что у instance есть id
                        message=instance.message  # Убедитесь, что message доступен
                    )


                except Profile.DoesNotExist:
                    print(f"User with id {user_id} does not exist.")

                except Exception as e:
                    # Если одна операция не удалась, остальные не прерываются
                    print(f"Error creating notification for user {user_id}: {str(e)}")

@receiver(post_save, sender=Coursesertificateuser)
def generate_certificate(sender, instance, created, **kwargs):
    if created:
        # Получаем курс, к которому относится сертификат
        course = instance.course.course  # Это поле course в модели Coursesertificate, которое ссылается на Course

        # Генерация сертификата
        certificate_file = generate_certificate_for_user(instance.user, course)

        # Сохраняем сгенерированный сертификат в поле certificate
        instance.certificate.save(
            f"{instance.user.id}_{instance.course.id}_certificate.webp",  # имя файла
            ContentFile(certificate_file.read()),  # содержание файла
            save=False  # не сохраняем модель сразу, чтобы избежать лишних запросов в БД
        )

        # Сохраняем модель после того, как файл будет прикреплен
        instance.save()


def get_student_marks(user, course):
    total_points = 0

    # Получаем все темы, связанные с этим курсом
    themes = course.themescourse.all()

    for theme in themes:
        # Получаем все вопросы для этой темы с статусом '1' (сданные вопросы)
        questions = theme.themes_questions.filter(status=1)  # Используем themes_questions вместо themequestion_set

        # Складываем все баллы для сданных вопросов
        for question in questions:
            total_points += question.point
    return total_points
    # Пример перевода баллов в оценку (это можно настроить)




MONTHS_RU = [
    "Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
    "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"
]

def generate_certificate_for_user(user, course):
    """
    Генерирует сертификат в формате WebP для пользователя по курсу.
    """
    # Получаем первый сертификат для курса
    certificate = Coursesertificate.objects.filter(course=course).first()

    if not certificate:
        raise ValueError("Сертификат для этого курса не найден.")

    # Проверяем наличие фонового изображения
    certificate_template_path = certificate.previev.path if certificate.previev else None
    if not certificate_template_path:
        raise ValueError("У сертификата отсутствует фоновое изображение.")

    # Проверяем наличие размеров для сертификата
    width, height = certificate.width, certificate.height
    if not width or not height:
        raise ValueError("Размеры сертификата не указаны.")

    # Подготовим описание сертификата из RichTextField
    certificate_description = certificate.description

    # Форматируем дату в русский формат: ДД Месяц ГГГГ
    certificate_create_date = certificate.create
    day = certificate_create_date.day
    month = MONTHS_RU[certificate_create_date.month - 1]  # Месяцы с 0 индексируются, поэтому вычитаем 1
    year = certificate_create_date.year
    formatted_date = f"{day} {month} {year}"

    # Подготовим значения для замены в шаблоне
    context = {
        "certificate_student_name": user.name,
        "certificate_course": course.name,
        "certificate_student_marks": get_student_marks(user, course),
        "certificate_student_date": formatted_date,  # Используем отформатированную дату
        "certificate_student_email": user.email,
        "certificate_code": generate_unique_code(user, course),
        "certificate_student_photo": user.avatar.path if user.avatar else None,
    }

    # Заменяем плейсхолдеры в описании на реальные данные
    rendered_description = replace_certificate_placeholders(certificate_description, context)

    # Создаём изображение сертификата
    certificate_image = create_certificate_with_html2image(
        template_path=certificate_template_path,
        html_content=rendered_description,
        size=(width, height)
    )

    # Конвертируем изображение в WebP
    buffer = BytesIO()
    certificate_image.save(buffer, format="WEBP", quality=95)  # Устанавливаем качество
    buffer.seek(0)  # Возвращаем курсор в начало

    # Возвращаем WebP как файл
    webp_file = ContentFile(buffer.getvalue())
    return webp_file


def create_certificate_with_html2image(template_path, html_content, size):
    """
    Создаёт изображение сертификата с рендерингом HTML-текста поверх фонового изображения.
    """
    # Загружаем изображение фона
    base_image = Image.open(template_path).convert("RGBA")
    base_image = base_image.resize(size, Image.Resampling.LANCZOS)

    # Создаём временный HTML-файл
    temp_html_path = "temp_certificate.html"
    with open(temp_html_path, "w", encoding="utf-8") as temp_html:
        temp_html.write(f"""
        <html>
        <body style="margin: 0; padding: 0; width: {size[0]}px; height: {size[1]}px; position: relative;">
            {html_content}
        </body>
        </html>
        """)

    # Рендерим HTML в изображение с помощью html2image
    hti = Html2Image(output_path=".")
    rendered_image_path = "certificate_rendered.png"
    hti.screenshot(
        html_file=temp_html_path,
        save_as=rendered_image_path,
        size=size
    )

    # Загружаем сгенерированное изображение текста
    rendered_image = Image.open(rendered_image_path).convert("RGBA")

    # Накладываем текстовое изображение поверх фона
    combined_image = Image.alpha_composite(base_image, rendered_image)

    # Удаляем временные файлы
    os.remove(temp_html_path)
    os.remove(rendered_image_path)

    return combined_image

def replace_certificate_placeholders(certificate_description, context):
    """
    Заменяет плейсхолдеры вида [certificate_student_name] на реальные данные.
    """
    rendered = certificate_description

    for key, value in context.items():
        placeholder = f"[{key}]"
        if key == "certificate_student_photo" and value:  # Если это фото, преобразуем в base64
            # Преобразуем фото в base64
            with open(value, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            # Вставляем base64-строку в тег <img>
            value = f'<img src="data:image/jpeg;base64,{img_base64}" alt="Student Photo" style="max-width:50px; height:auto;" />'
        rendered = rendered.replace(placeholder, str(value))

    return rendered

def generate_unique_code(user, course):
    """
    Генерация уникального 6-значного кода для сертификата, начиная с 100000.
    """
    # Генерируем случайное число в диапазоне от 100000 до 999999
    unique_code = random.randint(100000, 999999)

    return f"{unique_code}"