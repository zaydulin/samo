
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.http import JsonResponse
from conference.models import VideoChatRoom , VideoChatUser


# Create your views here.

class RequestToConference(TemplateView):
    template_name = 'conference/requesttoconference.html'

    def get(self, request, *args, **kwargs):
        slug = request.GET.get('slug')
        current_user = request.user
        room = VideoChatRoom.objects.get(slug=slug)
        user_instance, _ = VideoChatUser.objects.get_or_create(user=current_user)

        if room.type == 2 and room.is_closed:
            return super().get(request, *args, **kwargs)

        if room.type == 1 and room.is_start:
            return redirect(reverse('useraccount:video_chat_root', kwargs={'slug': room.slug}))

        if room.visitors.filter(id=user_instance.id).exists() or room.participants.filter(id=user_instance.id).exists():
            return redirect(reverse('useraccount:video_chat_root', kwargs={'slug': room.slug}))

        # Убедитесь, что пользователь не перенаправляется повторно
        if not room.notadded.filter(id=user_instance.id).exists():
            if not room.visitors.filter(id=user_instance.id).exists() and not room.participants.filter(id=user_instance.id).exists():
                room.notadded.add(user_instance)
            else:
                room.visitors.remove(user_instance)
                room.participants.remove(user_instance)
                room.notadded.add(user_instance)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.request.GET.get('slug')
        room = VideoChatRoom.objects.get(slug=slug)
        user_instance = VideoChatUser.objects.get(user=self.request.user)
        context['videochat'] = room
        context['videochat_user_id'] = user_instance.id  # Добавляем ID текущего пользователя
        return context

    def post(self, request, *args, **kwargs):
        slug = request.POST.get('slug')
        token = request.POST.get('token', '')
        current_user = request.user

        try:
            room = VideoChatRoom.objects.get(slug=slug)
        except VideoChatRoom.DoesNotExist:
            return JsonResponse({'error': 'Комната не найдена.'}, status=404)

        if room.token != token:
            return JsonResponse({'error': 'Неверный пароль.'}, status=400)

        user_instance, created = VideoChatUser.objects.get_or_create(user=current_user)
        if room.visitors.filter(id=user_instance.id).exists():
            redirect_url = reverse('useraccount:video_chat_root', kwargs={'slug': room.slug})
            return JsonResponse({'redirect': redirect_url})
        else:
            room.visitors.add(user_instance)
            room.notadded.remove(user_instance)
            redirect_url = reverse('useraccount:video_chat_root', kwargs={'slug': room.slug})
            return JsonResponse({'redirect': redirect_url})