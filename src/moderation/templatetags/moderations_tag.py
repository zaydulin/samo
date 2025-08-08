import random

from django import template
from pip._vendor.rich.theme import Theme

from lms.models import Needcourse, Themes,ThemesQuestion

register = template.Library()

register = template.Library()
@register.simple_tag
def get_notifications_count(user):
    if user.is_authenticated:
        notification = Needcourse.objects.filter(type=1).first()
        if notification:
            return Needcourse.objects.filter(type=1).count()
    return 0



@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None  # или можно вернуть какое-то значение по умолчанию


@register.simple_tag
def get_access_to_theme(theme_id, request):
    try:
        # Получаем тему по ID
        theme = Themes.objects.get(id=theme_id)
        if theme.access_type:
            previous_theme = Themes.objects.filter(
                modules=theme.modules,
                position__lt=theme.position
            ).order_by('-position').first()

            # Если предыдущая тема найдена
            if previous_theme:
                try:
                    theme_question = ThemesQuestion.objects.filter(
                        themes=previous_theme,
                        user=request.user
                    ).last()
                    if theme_question:
                        if theme_question.status != 1:  # 1 = "Прошел"
                            return False
                        else:
                            return True
                except ThemesQuestion.DoesNotExist:
                    return False
            else:
                return True
        else:
            return True
    except Themes.DoesNotExist:
        return False

@register.simple_tag
def get_theme_status(theme_id, request):
    try:
        # Получаем тему по ID
        theme = Themes.objects.get(id=theme_id)
        theme_question = ThemesQuestion.objects.filter(
            themes=theme,
            user=request.user
        ).last()
        if theme_question:
            if theme_question.status != 1:  # 1 = "Прошел"
                return False
            else:
                return True
        else:
            return False
    except Themes.DoesNotExist:
        return False


@register.filter
def shuffle(value):
    """Перемешивает список элементов."""
    if isinstance(value, list):
        shuffled = value[:]
        random.shuffle(shuffled)
        return shuffled
    return value