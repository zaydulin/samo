from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import VideoChatRoom, VideoChatUser
import json
from django.urls import reverse as django_reverse

@receiver(m2m_changed, sender=VideoChatRoom.notadded.through)
def notadded_changed(sender, instance, action, reverse, pk_set, **kwargs):
    print(f"[SIGNAL] Action: {action}, PK_SET: {pk_set}")
    channel_layer = get_channel_layer()
    group_name = f'notadded_{instance.slug}'

    if action == 'post_add':
        for pk in pk_set:
            try:
                videochat_user = VideoChatUser.objects.get(pk=pk)
                user_data = {
                    'id': videochat_user.id,
                    'username': videochat_user.user.username,
                    'avatar_url': videochat_user.user.avatar.url if videochat_user.user.avatar else '',
                }
                print(f"[SIGNAL] Добавление пользователя: {user_data['username']}")
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'add_user',
                        'user': user_data,
                    }
                )
            except VideoChatUser.DoesNotExist:
                continue

    elif action == 'post_remove':
        for pk in pk_set:
            print(f"[SIGNAL] Удаление пользователя ID: {pk}")
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'update_notadded',
                    'videochat_user_id': pk,
                }
            )
            try:
                videochat_user = VideoChatUser.objects.get(pk=pk)
                redirect_url = django_reverse('useraccount:video_chat_root', kwargs={'slug': instance.slug})
                # Отправляем сообщение в личную группу пользователя для перенаправления
                user_group = f'user_{videochat_user.user.id}'
                async_to_sync(channel_layer.group_send)(
                    user_group,
                    {
                        'type': 'user_allowed',
                        'redirect_url': redirect_url,
                    }
                )
            except VideoChatUser.DoesNotExist:
                continue

    elif action == 'post_clear':
        print("[SIGNAL] Очистка списка notadded.")
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'clear_notadded',
            }
        )