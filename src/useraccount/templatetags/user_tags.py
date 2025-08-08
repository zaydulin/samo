from django import template
from django.db.models import Q, Max, Subquery, OuterRef
from useraccount.models import Notification, Chat, ChatMessage
from moderation.models import Ticket

register = template.Library()
@register.simple_tag
def get_notifications_count(user):
    if user.is_authenticated:
        notification = Notification.objects.filter(user=user, status=1).first()
        if notification:
            return Notification.objects.filter(user=user, status=1).count()
    return 0

@register.simple_tag
def get_unread_notifications(user):
    if user.is_authenticated:
        return Notification.objects.filter(user=user, status=1).order_by('-created_at')[:4]
    return []

@register.simple_tag
def get_tickets_count(user):
    if user.is_authenticated:
        # Проверяем, есть ли тикеты, где пользователь является менеджером и статус равен 0 (Новое)
        notification = Ticket.objects.filter(manager=user, status=0).first()
        if notification:
            # Если есть новые тикеты, возвращаем количество тикетов со статусом 1 (Обратная связь)
            return Ticket.objects.filter(manager=user, status=0).count()
    return 0

@register.simple_tag(takes_context=True)
def unread_chats_count(context):
    user = context['user']  # Предполагается, что 'user' доступен в контексте

    # Получаем список чатов, в которых пользователь участвует
    user_chats = Chat.objects.filter(users=user)

    # Список чатов, в которых есть последние сообщения пользователя, которые он не прочитал
    unread_chats = []
    for chat in user_chats:
        last_message = chat.chatmessage.exclude(views=user).order_by('-date').first()
        if last_message:
            unread_chats.append(chat)

    # Возвращаем количество непрочитанных чатов
    return len(unread_chats)

