from django import template

register = template.Library()


# Ограничение на показ ссылки-кнопки Пользователи, если types включает указанный тип
@register.simple_tag(takes_context=True)
def user_has_access(context, access_type):
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return False
    user = request.user
    user_groups = user.groupuser.all()

    for group in user_groups:
        if str(access_type) in group.types:
            return True

    return False