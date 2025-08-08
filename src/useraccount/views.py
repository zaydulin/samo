import re

from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash, login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.utils import timezone
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_POST
from conference.models import  VideoChatRoom, VideoChatMessages, VideoChatFile, VideoChatUser
from conference.forms import  VideoChatRoomForm
from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView, ListView, CreateView, TemplateView
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
import logging

from moderation.models import Ticket
from .forms import *
from useraccount.models import History, Bookmark, Notebook, Schedule
from webmain.models import Blogs, Seo

logger = logging.getLogger(__name__)
from aiortc.contrib.media import MediaRelay
relay = MediaRelay()
peer_connections = {}
from django.shortcuts import render
from django.http import JsonResponse
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay
import asyncio
import json
from lms.models import Course, Courseuser
from django.db.models import Count, Sum
from django.contrib.contenttypes.models import ContentType

PEER_CONNECTIONS = {}


def stream_publisher(request):
    if request.method == 'GET':
        return render(request, 'useraccounts/publish.html')
    elif request.method == 'POST':
        offer = json.loads(request.body)

        pc = RTCPeerConnection()
        pc_id = "publisher"
        PEER_CONNECTIONS[pc_id] = pc

        relay = MediaRelay()

        @pc.on("iceconnectionstatechange")
        async def on_iceconnectionstatechange():
            if pc.iceConnectionState == "failed":
                await pc.close()

        @pc.on("track")
        def on_track(track):
            if track.kind == "video":
                pc.addTrack(relay.subscribe(track))

        asyncio.run(pc.setRemoteDescription(RTCSessionDescription(offer["sdp"], "offer")))
        answer = asyncio.run(pc.createAnswer())
        asyncio.run(pc.setLocalDescription(answer))

        return JsonResponse({"sdp": pc.localDescription.sdp})


def stream_viewer(request, user_id):
    if request.method == 'GET':
        return render(request, 'useraccounts/view.html')
    elif request.method == 'POST':
        pc = PEER_CONNECTIONS.get("publisher")

        if not pc:
            return JsonResponse({"error": "No publisher found for this user"})

        offer = json.loads(request.body)
        asyncio.run(pc.setRemoteDescription(RTCSessionDescription(offer["sdp"], "offer")))
        answer = asyncio.run(pc.createAnswer())
        asyncio.run(pc.setLocalDescription(answer))

        return JsonResponse({"sdp": pc.localDescription.sdp})


class VideoChatRoomDetailsView(DetailView):
    model = VideoChatRoom
    context_object_name = 'videochat'

    def dispatch(self, request, *args, **kwargs):
        # Get the VideoChatRoom object
        video_chat_room = self.get_object()

        # If the room is public, allow access
        if video_chat_room.type == 1 and video_chat_room.is_start:
            return super().dispatch(request, *args, **kwargs)


        if request.user.is_authenticated:
            current_user = request.user
            user_instance, _ = VideoChatUser.objects.get_or_create(user=current_user)
            if video_chat_room.spiker.id == current_user.id :
                return super().dispatch(request, *args, **kwargs)
            if video_chat_room.type == 1 and not video_chat_room.is_start:
                url = reverse('conference:request_access')
                full_url = f'{url}?slug={video_chat_room.slug}'
                video_chat_room.notadded.add(user_instance)
                return HttpResponseRedirect(full_url)

            if video_chat_room.type == 2 and  video_chat_room.is_closed:
                url = reverse('conference:request_access')
                full_url = f'{url}?slug={video_chat_room.slug}'
                video_chat_room.notadded.add(user_instance)
                return HttpResponseRedirect(full_url)

            if not video_chat_room.visitors.filter(id=user_instance.id).exists() and not video_chat_room.participants.filter(id=user_instance.id).exists():
                url = reverse('conference:request_access')
                full_url = f'{url}?slug={video_chat_room.slug}'
                video_chat_room.notadded.add(user_instance)
                return HttpResponseRedirect(full_url)

        else:
            login_url = reverse('useraccount:login')  # Укажите URL для страницы логина
            return HttpResponseRedirect(f'{login_url}?next={request.path}')

        # Otherwise, allow access
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        # Определение шаблона в зависимости от состояния авторизации пользователя
        if self.request.user.is_authenticated:
            return ['useraccounts/videochatroom_detail.html']
        else:
            return ['useraccounts/videochatroom_detail_nouser.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        videochat = self.get_object()
        # Список всех участников
        context['participants'] = videochat.participants.all()
        # Список всех участников
        context['visitors'] = videochat.visitors.all()
        # Список сообщений
        context['messages'] = VideoChatMessages.objects.filter(videoroom=videochat)
        # Список файлов
        context['files'] = VideoChatFile.objects.filter(videoroom=videochat)
        # Определяет текущего пользователя
        context['current_user'] = self.request.user
        # Передаем статус комнаты в контекст
        context['is_closed'] = videochat.is_closed
        context['is_start'] = videochat.is_start
        # Определяем, является ли текущий пользователь спикером
        context['is_spiker'] = videochat.spiker == self.request.user

        return context


class AddNotAddedView(DetailView):
    model = VideoChatRoom
    context_object_name = 'videochat'
    template_name = 'useraccounts/add_notadded.html'

    # def dispatch(self, request, *args, **kwargs):
    #     # Получаем объект VideoChatRoom по токену из URL
    #     token = kwargs.get('token')
    #     video_chat_room = get_object_or_404(VideoChatRoom, token=token)
    #
    #     # Получаем или создаем VideoChatUser для текущего пользователя
    #     current_user = request.user
    #     user_instance, _ = VideoChatUser.objects.get_or_create(user=current_user)
    #
    #     # Если пользователь не в 'notadded', добавляем его
    #     if user_instance not in video_chat_room.notadded.all():
    #         video_chat_room.notadded.add(user_instance)
    #
    #     # Если пользователь уже в 'notadded', перенаправляем на страницу видео-чата
    #     return HttpResponseRedirect(reverse('conference:video_chat_root', kwargs={'slug': video_chat_room.slug}))

    # Этот метод извлекает объект на основе токена
    def get_object(self, queryset=None):
        token = self.kwargs.get('token')
        try:
            # Получить доступ к видеочату с помощью токена
            return VideoChatRoom.objects.get(token=token)
        except VideoChatRoom.DoesNotExist:
            # Если ни один номер не соответствует заданному токену, выдается сообщение об ошибке 404
            raise Http404("VideoChatRoom with the provided token does not exist")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        videochat = self.get_object()
        # Список всех участников
        context['notadded'] = videochat.notadded.all()
        # Список файлов
        context['files'] = VideoChatFile.objects.filter(videoroom=videochat)
        # Определяет текущего пользователя
        context['current_user'] = self.request.user

        return context

    def post(self, request, *args, **kwargs):
        token = kwargs.get('token')
        video_chat_room = get_object_or_404(VideoChatRoom, token=token)
        current_user = request.user

        # Получить или создать экземпляр VideoChatUser для текущего пользователя
        user_instance, _ = VideoChatUser.objects.get_or_create(user=current_user)

        # Добавить в 'notadded', если его там еще нет
        if user_instance not in video_chat_room.notadded.all():
            video_chat_room.notadded.add(user_instance)

        # Перенаправление обратно на предыдущую страницу
        previous_url = request.META.get('HTTP_REFERER', '/')
        return HttpResponseRedirect(previous_url)


class SendMessageView(View):
    def post(self, request, *args, **kwargs):
        videochat_id = kwargs.get('pk')  # Получаем ID видеочата
        content = request.POST.get('content')  # Получаем содержимое сообщения

        # Проверяем, что видеочат существует
        try:
            videochat = VideoChatRoom.objects.get(id=videochat_id)
        except ObjectDoesNotExist:
            return JsonResponse({"status": "error", "message": "Видеочат не найден."}, status=404)

        # Создаем новое сообщение
        message = VideoChatMessages.objects.create(
            author=request.user,  # Автор сообщения
            videoroom=videochat,  # К какому видеочату принадлежит сообщение
            content=content,  # Содержимое сообщения
        )

        # Возвращаем успешный ответ
        return JsonResponse({"status": "ok", "message": "Сообщение отправлено."})


class ToggleVideoChatRoomStatus(View):
    def post(self, request, *args, **kwargs):
        videochat_id = kwargs.get('pk')  # Получить ID объекта
        videochat = VideoChatRoom.objects.get(pk=videochat_id)

        field = request.POST.get('field')  # Название поля для смены
        if field in ['is_closed', 'is_start']:
            # Сменить значение поля
            current_value = getattr(videochat, field)
            setattr(videochat, field, not current_value)  # Смена состояния
            videochat.save()

            return JsonResponse({'status': 'ok', 'field': field, 'new_value': not current_value})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid field'}, status=400)


class AddUserToGroup(View):
    def post(self, request, *args, **kwargs):
        videochat_id = kwargs.get('pk')
        videochat = VideoChatRoom.objects.get(pk=videochat_id)

        user_id = request.POST.get("user_id")
        user = VideoChatUser.objects.get(pk=user_id)

        group = request.POST.get("group")

        if group not in ["visitors", "participants"]:
            return JsonResponse({"status": "error", "message": "Invalid group"}, status=400)

        # Удалить из notadded и добавить в нужную группу
        if group == "visitors":
            videochat.visitors.add(user)
        elif group == "participants":
            videochat.participants.add(user)

        videochat.notadded.remove(user)  # Удалить из notadded

        return JsonResponse({"status": "ok", "group": group})


class UpdateGroup(View):
    def post(self, request, *args, **kwargs):
        videochat_id = kwargs.get('pk')
        videochat = VideoChatRoom.objects.get(pk=videochat_id)

        user_id = request.POST.get("user_id")
        user = VideoChatUser.objects.get(pk=user_id)

        action = request.POST.get("action")

        if action == "remove_participant":
            videochat.participants.remove(user)

        elif action == "add_to_notadded":
            videochat.notadded.add(user)  # Добавляем в notadded
            videochat.visitors.remove(user)  # Удаляем из visitors
            videochat.participants.remove(user)  # Удаляем из participants


        elif action == "pin_primary":
            if user in videochat.primary.all():  # Если пользователь уже в primary
                videochat.primary.remove(user)  # Убираем его из primary
                videochat.participants.add(user)  # Удаляем из participants
            else:
                videochat.primary.add(user)  # Добавляем в primary
                videochat.participants.remove(user)  # Удаляем из participants

        else:
            return JsonResponse({"status": "error", "message": "Invalid action"}, status=400)

        return JsonResponse({"status": "ok", "action": action})


class UpdateMyGroup(View):
    def post(self, request, *args, **kwargs):
        videochat_id = kwargs.get('pk')
        videochat = VideoChatRoom.objects.get(pk=videochat_id)

        user_id = request.POST.get("user_id")
        user = VideoChatUser.objects.get(pk=user_id)

        action = request.POST.get("action")

        if action == "remove_participant":
            videochat.participants.remove(user)

        elif action == "add_to_notadded":
            videochat.notadded.add(user)  # Добавляем в notadded
            videochat.visitors.remove(user)  # Удаляем из visitors
            videochat.participants.remove(user)  # Удаляем из participants

        else:
            return JsonResponse({"status": "error", "message": "Invalid action"}, status=400)

        return JsonResponse({"status": "ok", "action": action})


class UpdateUserFieldView(View):
    def post(self, request, user_id):
        field = request.POST.get('field')  # Получаем поле, которое нужно изменить

        try:
            user = VideoChatUser.objects.get(id=user_id)  # Получаем пользователя по ID

            # Переключаем соответствующее поле
            if field == 'sound_root':
                user.sound_root = not user.sound_root
            elif field == 'video_root':
                user.video_root = not user.video_root
            elif field == 'hand':
                user.hand = not user.hand
            if field == 'saved_video':
                user.saved_video = not user.saved_video
            user.save()

            return JsonResponse({
                'status': 'ok',
                'field': field,
                'new_value': getattr(user, field),  # Передаем новое значение поля
                'message': f"Поле '{field}' успешно обновлено.",
            })
        except VideoChatUser.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Пользователь не найден.',
            })


class UpdateMyUserFieldView(View):
    def post(self, request, user_id):
        field = request.POST.get('field')  # Получаем поле, которое нужно изменить

        try:
            user = VideoChatUser.objects.get(id=user_id)  # Получаем текущего пользователя

            # Переключаем соответствующее поле
            if field == 'sound':
                user.sound = not user.sound
            elif field == 'video':
                user.video = not user.video
            elif field == 'hand':
                user.hand = not user.hand
            if field == 'desktop':
                user.desktop = not user.desktop
            user.save()

            return JsonResponse({
                'status': 'ok',
                'field': field,
                'new_value': getattr(user, field),  # Передаем новое значение поля
                'message': f"Поле '{field}' успешно обновлено.",
            })
        except VideoChatUser.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Пользователь не найден.',
            })

class VideoChatRoomView(ListView):
    model = VideoChatRoom
    template_name = 'useraccounts/videochatroom_list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chatrooms = VideoChatRoom.objects.filter(spiker=self.request.user)
        conferences = []
        for room in chatrooms:
            if room.end_data:
                end_date = room.end_data.strftime('%Y-%m-%d') if room.end_data else room.start_data.strftime('%Y-%m-%d')
            conference = {
                'title': room.name,


                'roomslug': room.slug,
                'className': 'bg-primary'
            }
            conferences.append(conference)
        context['conferences_json'] = json.dumps(conferences)
        context['chatrooms'] = chatrooms
        return context


class CreateVideoChatRoomView(CreateView):
    model = VideoChatRoom
    form_class = VideoChatRoomForm
    template_name = 'useraccounts/create_video_chat_room.html'

    def get_success_url(self):
        # Получаем course_id из URL
        course_id = self.kwargs['course_id']
        # Формируем URL для success_url с передачей course_id
        return reverse_lazy('moderation:conferences_list', kwargs={'course_id': course_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем курс по course_id из URL
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)
        context['course'] = course
        return context

    def form_valid(self, form):
        # Устанавливаем курс в модель VideoChatRoom
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)
        form.instance.course = course  # Присваиваем курс в модель
        form.instance.spiker = self.request.user
        return super().form_valid(form)
class VideoChatRoomSearchView(ListView):
    model = VideoChatRoom
    template_name = "useraccounts/conferencesearch.html"
    context_object_name = "chat_rooms"

    def get_queryset(self):
        token = self.request.GET.get("token", None)
        queryset = VideoChatRoom.objects.all()
        if token:
            queryset = queryset.filter(token=token)
        return queryset

class ConferenceDashboardView(ListView):
    model = VideoChatRoom
    template_name = 'useraccounts/dashboard_conf.html'
    context_object_name = 'useraccount:conferencedashboard'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the current user and corresponding VideoChatUser
        current_user = self.request.user
        video_chat_user = VideoChatUser.objects.filter(user=current_user).first()

        # Compute the counts for spiker, participant, and visitor roles
        spiker_count = VideoChatRoom.objects.filter(spiker=current_user).count()
        participant_count = VideoChatRoom.objects.filter(participants=video_chat_user).distinct().count()
        visitor_count = VideoChatRoom.objects.filter(visitors=video_chat_user).distinct().count()

        # Add these counts to the context
        context['spiker_count'] = spiker_count
        context['participant_count'] = participant_count
        context['visitor_count'] = visitor_count

        return context

class TestTemplateView(TemplateView):
    template_name = 'testvideo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room_slug'] = 'room1'  # или динамически определить
        return context


class FeedView(LoginRequiredMixin,TemplateView):
    template_name = 'useraccounts/feed.html'

    @staticmethod
    def clean_description(description):
        """Удаляет теги <img> и заменяет их на <Изображение>, но сохраняет остальной HTML"""
        if not description:
            return ""

        # Заменяем все <img> теги на <Изображение>
        description = re.sub(r'<img[^>]+>', ' <Изображение>', description, flags=re.IGNORECASE)

        return mark_safe(description.strip())  # Делаем HTML безопасным

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        page = int(self.request.GET.get('page', 1))
        per_page = 20

        feed_items = []

        if user.is_authenticated:
            blog_content_type = ContentType.objects.get_for_model(Blogs)
            user_blog_history_ids = History.objects.filter(
                user=user, content_type=blog_content_type
            ).values_list('object_id', flat=True)

            if user_blog_history_ids:
                blogs = Blogs.objects.filter(id__in=user_blog_history_ids).annotate(
                    history_count=Count('id')
                ).order_by('-history_count')[:20]
                if blogs.exists():
                    category_ids = blogs.values_list('category__id', flat=True)
                    related_blogs = Blogs.objects.filter(
                        category__id__in=category_ids
                    ).exclude(id__in=user_blog_history_ids).order_by('-pageviews')[:20]
                    blogs = list(blogs) + list(related_blogs)
            else:
                blogs = list(Blogs.objects.all().order_by('-pageviews'))

            course_content_type = ContentType.objects.get_for_model(Course)
            user_course_history_ids = History.objects.filter(
                user=user, content_type=course_content_type
            ).values_list('object_id', flat=True)

            if user_course_history_ids:
                courses = Course.objects.filter(id__in=user_course_history_ids).annotate(
                    history_count=Count('id')
                ).order_by('-history_count')[:20]
                if courses.exists():
                    category_ids = courses.values_list('category__id', flat=True)
                    related_courses = Course.objects.filter(
                        category__id__in=category_ids
                    ).exclude(id__in=user_course_history_ids).order_by('-pageviews')[:20]
                    courses = list(courses) + list(related_courses)
            else:
                courses = list(Course.objects.all().order_by('-pageviews'))
        else:
            blogs = list(Blogs.objects.all().order_by('-pageviews'))
            courses = list(Course.objects.all().order_by('-pageviews'))

        feed_items = blogs + courses
        feed_items = sorted(feed_items, key=lambda x: x.pageviews, reverse=True)  # Общая сортировка по просмотрам

        paginator = Paginator(feed_items, per_page)
        page_obj = paginator.get_page(page)

        # Очищаем description перед отправкой в шаблон
        for item in page_obj:
            if hasattr(item, 'description'):
                item.description = self.clean_description(item.description)

        context['feed_items'] = page_obj
        return context

    def get(self, request, *args, **kwargs):
        """Обрабатывает AJAX-запросы и возвращает JSON"""
        if request.GET.get("ajax"):
            context = self.get_context_data(**kwargs)
            page_obj = context["feed_items"]
            return JsonResponse({
                "items": [
                    {
                        "url": item.get_absolute_url() if callable(getattr(item, 'get_absolute_url', None)) else "",
                        "author": str(item.author) if hasattr(item, 'author') else "",
                        "create": item.create.strftime('%Y-%m-%d %H:%M:%S') if hasattr(item, 'create') else "",
                        "description": str(item.description) if hasattr(item, 'description') else "",
                        "previev": item.previev.url if hasattr(item, 'previev') and item.previev else None,
                        "pageviews": item.pageviews if hasattr(item, 'pageviews') else 0
                    }
                    for item in page_obj
                ],
                "has_next": page_obj.has_next()
            }, safe=False)

        return super().get(request, *args, **kwargs)


@login_required
@require_POST
def add_bookmark(request):
    content_type_str = request.POST.get('content_type')
    object_id = request.POST.get('object_id')

    if not content_type_str or not object_id:
        return JsonResponse({'status': 'error', 'message': 'Invalid data.'}, status=400)

    try:
        content_type = ContentType.objects.get(model=content_type_str)
    except ContentType.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid content type.'}, status=400)

    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        content_type=content_type,
        object_id=object_id
    )

    return JsonResponse({'status': 'success', 'created': created})


@login_required
@require_POST
def remove_bookmark(request):
    content_type_str = request.POST.get('content_type')
    object_id = request.POST.get('object_id')

    if not content_type_str or not object_id:
        return JsonResponse({'status': 'error', 'message': 'Invalid data.'}, status=400)

    try:
        content_type = ContentType.objects.get(model=content_type_str)
    except ContentType.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid content type.'}, status=400)

    deleted, _ = Bookmark.objects.filter(
        user=request.user,
        content_type=content_type,
        object_id=object_id
    ).delete()

    return JsonResponse({'status': 'success', 'deleted': deleted > 0})

class BookmarkListView(LoginRequiredMixin, ListView):
    model = Bookmark
    template_name = 'useraccounts/bookmark_list.html'
    context_object_name = 'bookmarks'
    paginate_by = 10

    @staticmethod
    def clean_description(description):
        """Удаляет теги <img> и заменяет их на <Изображение>, но сохраняет остальной HTML"""
        if not description:
            return ""

        # Заменяем все <img> теги на <Изображение>
        description = re.sub(r'<img[^>]+>', ' <Изображение>', description, flags=re.IGNORECASE)

        return mark_safe(description.strip())  # Делаем HTML безопасным

    def get_queryset(self):
        bookmarks = Bookmark.objects.filter(user=self.request.user).select_related("content_type")
        for bookmark in bookmarks:
            if hasattr(bookmark.content_object, 'description'):
                bookmark.content_object.description = self.clean_description(bookmark.content_object.description)
        return bookmarks

class DeleteBookmarkView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        bookmark_id = request.POST.get('bookmark_id')
        try:
            bookmark = Bookmark.objects.get(id=bookmark_id, user=request.user)
            bookmark.delete()
            return JsonResponse({'success': True})
        except Bookmark.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Закладка не найдено'})


class NotebookListView(LoginRequiredMixin, View):
    template_name = 'useraccounts/notebook_list.html'
    paginate_by = 10  # Количество записей на странице

    def get(self, request, *args, **kwargs):
        notebooks = Notebook.objects.filter(
            user=request.user
        ).order_by('-period')

        notebooks_by_month = {}
        for notebook in notebooks:
            month_year = notebook.period.strftime('%Y-%m')
            if month_year not in notebooks_by_month:
                notebooks_by_month[month_year] = []
            notebooks_by_month[month_year].append(notebook)

        months_list = list(notebooks_by_month.keys())
        months_list.sort(reverse=True)

        current_month_year = request.GET.get('month')
        if current_month_year not in months_list:
            current_month_year = months_list[0] if months_list else None

        notebooks_for_month = notebooks_by_month.get(current_month_year, [])

        paginator = Paginator(notebooks_for_month, self.paginate_by)

        page = request.GET.get('page')
        try:
            notebooks_page = paginator.page(page)
        except PageNotAnInteger:
            notebooks_page = paginator.page(1)
        except EmptyPage:
            notebooks_page = paginator.page(paginator.num_pages)

        # Создаем экземпляр формы для создания новой записи
        notebook_form = NotebookForm()

        context = {
            'notebooks_page': notebooks_page,
            'months_list': months_list,
            'current_month_year': current_month_year,
            'notebook_form': notebook_form,  # Передаем форму в контекст шаблона
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        notebook_form = NotebookForm(request.POST)
        if notebook_form.is_valid():
            new_notebook = notebook_form.save(commit=False)
            new_notebook.user = request.user
            new_notebook.save()
            return redirect('useraccount:notebook_list')  # Перенаправляем на страницу с записями

        # Если форма невалидна, возвращаем страницу с формой и ошибками
        notebooks = Notebook.objects.filter(
            user=request.user
        ).order_by('-period')

        notebooks_by_month = {}
        for notebook in notebooks:
            month_year = notebook.period.strftime('%Y-%m')
            if month_year not in notebooks_by_month:
                notebooks_by_month[month_year] = []
            notebooks_by_month[month_year].append(notebook)

        months_list = list(notebooks_by_month.keys())
        months_list.sort(reverse=True)

        current_month_year = request.GET.get('month')
        if current_month_year not in months_list:
            current_month_year = months_list[0] if months_list else None

        notebooks_for_month = notebooks_by_month.get(current_month_year, [])

        paginator = Paginator(notebooks_for_month, self.paginate_by)

        page = request.GET.get('page')
        try:
            notebooks_page = paginator.page(page)
        except PageNotAnInteger:
            notebooks_page = paginator.page(1)
        except EmptyPage:
            notebooks_page = paginator.page(paginator.num_pages)

        context = {
            'notebooks_page': notebooks_page,
            'months_list': months_list,
            'current_month_year': current_month_year,
            'notebook_form': notebook_form,  # Передаем форму в контекст шаблона
        }
        return render(request, self.template_name, context)


class NotebookDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notebook = get_object_or_404(Notebook, pk=pk)
        if notebook.user == request.user:
            notebook.delete()
            return JsonResponse({'message': 'Notebook deleted successfully'}, status=200)
        else:
            return JsonResponse({'error': 'You do not have permission to delete this notebook'}, status=403)


@method_decorator(login_required, name='dispatch')
class NotebookEventsView(View):

    def get(self, request, *args, **kwargs):
        notebooks = Notebook.objects.filter(user=request.user)
        events = [
            {
                'title': notebook.name,
                'start': notebook.period.isoformat(),
                'description': notebook.description,
            } for notebook in notebooks
        ]
        return JsonResponse(events, safe=False)


class DashboardTeacher(LoginRequiredMixin, TemplateView):
    template_name = 'useraccounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()
        upcoming_days = today + timezone.timedelta(days=5)

        # Определяем текущий месяц и год
        current_month = today.month
        current_year = today.year

        # Получаем все курсы, созданные пользователем
        courses = Course.objects.filter(author=user)

        # Подсчёт количества закладок для курсов пользователя
        course_content_type = ContentType.objects.get_for_model(Course)
        bookmarks_count = Bookmark.objects.filter(
            content_type=course_content_type,
            object_id__in=courses.values_list('id', flat=True)
        ).count()

        # Подсчёт общего количества просмотров всех курсов пользователя
        total_pageviews = courses.aggregate(total_views=Sum('pageviews'))['total_views'] or 0

        # Подсчет количества конференций, которые проходят сегодня
        today_conferences_count = VideoChatRoom.objects.filter(start_data=today, spiker=user).count()

        # Выборка ближайших конференций (на 5 дней вперед)
        upcoming_conferences = VideoChatRoom.objects.filter(
            spiker=user,
            start_data__range=(today, upcoming_days)
        ).order_by('start_data', 'start_time')

        # Подсчёт количества расписаний для пользователя
        user_schedule_count = Schedule.objects.filter(user=user).count()

        # События в расписании на сегодня
        today_schedule = Schedule.objects.filter(user=user, data=today).order_by('time_start')

        # Ближайшие события в расписании (на 5 дней вперед)
        upcoming_schedule = Schedule.objects.filter(
            user=user,
            data__range=(today, upcoming_days)
        ).order_by('data', 'time_start')

        # Подсчет новых учеников (оплативших)
        new_students_count = Courseuser.objects.filter(
            course__in=courses, status=2
        ).count()

        # Подсчет заработка за текущий месяц
        monthly_earnings = Courseuser.objects.filter(
            course__in=courses,
            status=2,
            create__month=current_month,
            create__year=current_year
        ).aggregate(total_earnings=Sum('course__price'))['total_earnings'] or 0

        # Формирование данных для графика продаж (дата оплаты + сумма оплаты)
        course_sales = Courseuser.objects.filter(
            course__in=courses, status=2
        ).select_related('course').values('create', 'course__price')

        sales_data = {}
        for sale in course_sales:
            date_str = sale['create'].strftime("%d %b %Y")  # Форматируем дату
            price = sale['course__price']
            if date_str in sales_data:
                sales_data[date_str] += price  # Если уже есть дата, добавляем сумму
            else:
                sales_data[date_str] = price  # Если даты нет, создаем новую запись

        # Формируем JSON для графика
        sales_chart_data = {
            "monthDataSeries1": {
                "prices": list(sales_data.values()),
                "dates": list(sales_data.keys())
            }
        }

        # Фильтруем тикеты (все кроме 'Решенный' и 'Закрытый')
        open_tickets = Ticket.objects.filter(
            author=user
        ).exclude(status__in=[3, 4])  # Исключаем статусы 3 и 4

        context['user'] = user
        context['courses'] = courses
        context['bookmarks_count'] = bookmarks_count  # Количество закладок
        context['total_pageviews'] = total_pageviews  # Общее число просмотров курсов
        context['today_conferences_count'] = today_conferences_count  # Количество конференций сегодня
        context['upcoming_conferences'] = upcoming_conferences  # Список ближайших конференций
        context['user_schedule_count'] = user_schedule_count  # Количество событий в расписании пользователя
        context['today_schedule'] = today_schedule  # События в расписании на сегодня
        context['upcoming_schedule'] = upcoming_schedule  # События в расписании на ближайшие 5 дней
        context['new_students_count'] = new_students_count  # Количество новых учеников
        context['monthly_earnings'] = monthly_earnings  # Заработок за текущий месяц
        context['sales_chart_data'] = json.dumps(sales_chart_data)  # Данные для графика продаж
        context['open_tickets'] = open_tickets  # Незакрытые тикеты
        return context

class MyTicket(LoginRequiredMixin, TemplateView):
    template_name = 'useraccounts/mytikcets.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket = Ticket.objects.order_by('-date').filter(author=self.request.user)
        context['statuses'] = Ticket.STATUS_CHOICES
        user = self.request.user


        search_id = self.request.GET.get('search_id', '')
        if search_id:
            ticket = ticket.filter(id__icontains=search_id)

        search_type = self.request.GET.get('search_type', '')
        if search_type:
            ticket = ticket.filter(status=search_type)

        for_me = self.request.GET.get('for_me', '')
        if for_me:
            ticket = ticket.filter(manager=user)

        search_date = self.request.GET.get('search_date', '')
        if search_date:
            # Преобразуем строку даты в объект datetime
            try:
                search_date = timezone.datetime.strptime(search_date, '%Y-%m-%d').date()
                ticket = ticket.filter(date__date=search_date)
            except ValueError:
                pass

        # Пагинация
        paginator = Paginator(ticket, 10)  # 20 элементов на страницу
        page = self.request.GET.get('page')
        try:
            ticket_list = paginator.page(page)
        except PageNotAnInteger:
            ticket_list = paginator.page(1)
        except EmptyPage:
            ticket_list = paginator.page(paginator.num_pages)

        try:
            seo_data = Seo.objects.get(pagetype=6)
            context['seo_previev'] = seo_data.previev
            context['seo_title'] = seo_data.title
            context['seo_description'] = seo_data.description
            context['seo_propertytitle'] = seo_data.propertytitle
            context['seo_propertydescription'] = seo_data.propertydescription
        except Seo.DoesNotExist:
            context['seo_previev'] = None
            context['seo_title'] = None
            context['seo_description'] = None
            context['seo_propertytitle'] = None
            context['seo_propertydescription'] = None

        context['ticket_list'] = ticket_list  # Передаем отфильтрованные задачи
        context['tickets'] = ticket # Передаем отфильтрованные задачи
        context['paginator'] = paginator
        context['page_obj'] = ticket_list
        return context

class CreateMyTicket(LoginRequiredMixin, TemplateView):
    template_name = 'useraccounts/create_tikcets.html'

    def post(self, request, *args, **kwargs):
        ticket_theme = request.POST.get('ticket_theme')

        Ticket.objects.create(
            themas = ticket_theme,
            author = request.user,

        )


        return redirect(reverse('useraccount:user_tickets'))

def custom_logout(request):
    logout(request)
    return redirect('useraccount:login')

"""Личный кабинет"""
class EditMyProfileView(TemplateView, LoginRequiredMixin):
    template_name = 'moderations/profile_edit.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        initial_data = {'birthday': request.user.birthday.strftime('%Y-%m-%d') if request.user.birthday else None}
        form = UserProfileForm(instance=request.user, initial=initial_data)
        password_form = PasswordChangeForm(user=request.user)
        context = self.get_context_data(form=form,password_form=password_form, title='Личные данные')
        return self.render_to_response(context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if 'profile_form' in request.POST:  # Проверяем, отправлена ли форма профиля
            form = UserProfileForm(request.POST, request.FILES, instance=request.user)
            password_form = PasswordChangeForm(user=request.user)  # Передаем пустую форму для смены пароля

            if form.is_valid():
                form.save()
                messages.success(request, "Профиль обновлен успешно.")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Ошибка в поле {field}: {error}")
        elif 'password_form' in request.POST:  # Проверяем, отправлена ли форма смены пароля
            form = UserProfileForm(instance=request.user)  # Передаем пустую форму профиля
            password_form = PasswordChangeForm(data=request.POST, user=request.user)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Пароль изменен успешно.")
            else:
                for field, errors in password_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Ошибка в поле {field}: {error}")

        # Возвращаем формы в контекст, чтобы отобразить их на странице
        context = self.get_context_data(form=form, password_form=password_form, title='Личные данные')
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Вызов `super()` сохраняет функциональность `ListView`
        try:
            seo_data = Seo.objects.get(pagetype=6)
            context['seo_previev'] = seo_data.previev
            context['seo_title'] = seo_data.title
            context['seo_description'] = seo_data.description
            context['seo_propertytitle'] = seo_data.propertytitle
            context['seo_propertydescription'] = seo_data.propertydescription
        except Seo.DoesNotExist:
            context['seo_previev'] = None
            context['seo_title'] = None
            context['seo_description'] = None
            context['seo_propertytitle'] = None
            context['seo_propertydescription'] = None
        return context
"""Регистрация/Авторизация"""

class CustomLoginView(auth_views.LoginView):
    template_name = 'useraccounts/userauth/login.html'
    form_class = CustomAuthenticationForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(reverse('useraccount:edit_profile'))

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        user_type = self.request.user.type
        next = self.request.GET.get('next')
        if next:
            return next
        return reverse('useraccount:edit_profile')

    def form_invalid(self, form):
        # Обрабатываем неуспешную аутентификацию
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            seo_data = Seo.objects.get(pagetype=5)
            context.update({
                'seo_previev': seo_data.previev,
                'seo_title': seo_data.title,
                'seo_description': seo_data.metadescription,
                'seo_propertytitle': seo_data.propertytitle,
                'seo_propertydescription': seo_data.propertydescription,
            })
        except Seo.DoesNotExist:
            context.update({
                'seo_previev': None,
                'seo_title': None,
                'seo_description': None,
                'seo_propertytitle': None,
                'seo_propertydescription': None,
            })
        return context


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'useraccounts/userauth/signup.html'
    success_url = reverse_lazy('useraccount:login')  # URL для редиректа после успешной регистрации

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(reverse('useraccount:edit_profile'))

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        # Возвращаем success_url, можно переопределить логику, если нужно
        return self.success_url

    def get_form_kwargs(self):
        # Передаем дополнительные аргументы в форму, если требуется
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Убедитесь, что форма поддерживает user
        return kwargs

    def form_valid(self, form):
        # Сохраняем пользователя
        user = form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')

        # Аутентифицируем пользователя
        user = authenticate(username=username, password=password)
        if user is not None:
            # Входим в систему
            login(self.request, user)
            return redirect(self.get_success_url())
        else:
            # Возвращаем ошибку, если аутентификация не удалась
            return HttpResponseServerError('Ошибка аутентификации')

    def get_context_data(self, **kwargs):
        # Добавляем данные для SEO
        context = super().get_context_data(**kwargs)
        try:
            seo_data = Seo.objects.get(pagetype=6)
            context['seo_previev'] = seo_data.previev
            context['seo_title'] = seo_data.title
            context['seo_description'] = seo_data.metadescription
            context['seo_propertytitle'] = seo_data.propertytitle
            context['seo_propertydescription'] = seo_data.propertydescription
        except Seo.DoesNotExist:
            # Добавляем пустые значения, если SEO данных нет
            context.update({
                'seo_previev': None,
                'seo_title': None,
                'seo_description': None,
                'seo_propertytitle': None,
                'seo_propertydescription': None,
            })
        return context

class CustomPasswordResetView(PasswordResetView):
    template_name = 'useraccounts/userauth/restore_access.html'
    email_template_name = 'site/email/password_reset_email.html'
    subject_template_name = 'site/email/password_reset_subject.txt'
    form_class = PasswordResetEmailForm
    success_url = reverse_lazy('useraccount:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'useraccounts/userauth/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'moderations/restore_access_user.html'
    form_class = SetPasswordFormCustom
    success_url = reverse_lazy('useraccount:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'useraccounts/userauth/password_reset_complete.html'