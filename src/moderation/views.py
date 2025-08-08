import json
import random
import uuid
from datetime import datetime, timedelta
from itertools import zip_longest
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.forms import modelformset_factory, model_to_dict
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from collections import defaultdict
from django.forms import modelformset_factory, inlineformset_factory
import logging
from django.forms import formset_factory
import os
from django.db.models import Prefetch
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse, HttpResponseRedirect, FileResponse
from django.db import transaction, IntegrityError
from django.db.models import Q, Sum
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout, authenticate, login, get_user_model, update_session_auth_hash
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView, \
    PasswordResetDoneView
from django.urls import reverse_lazy
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
import re
import pandas as pd
from django.core.mail import send_mail
from django.db import connection
from django.contrib import messages
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView
from django.http import HttpResponseServerError, HttpResponseForbidden, JsonResponse, HttpResponseNotFound
from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.shortcuts import render
from django.db.models import F

from lms.models import CourseSettings, HomeWorkFiles, HomeWork, Qwiz, CourseAssistents, Files, Question,HintsToQuestion, CategorysCourse, Needcourse, Courserewievs, \
    Schedulestream, \
    Coursesertificateuser, Course, Courseuser, Coursecomments, Themes, Modules, Coursesertificate, ThemesQuestion
from django.db.models import Exists, OuterRef
from django.db.models import Q, Count, OuterRef, Subquery
from conference.models import VideoChatRoom
from useraccount.forms import SignUpForm, UserProfileForm, PasswordResetEmailForm, SetPasswordFormCustom, \
    CustomAuthenticationForm, NotebookForm
from webmain.models import Seo, Organizations, Jobs, SettingsGlobale, ContactPage, Faqs, Blogs, Categorys, Testimonial, \
    Pages
from moderation.forms import ThemesForm, FilesFormSet, StreamSessionFormSet, CategorysCourseForm, CourseForm, \
    CourseUpdateForm, AssumptioncourseForm, WorkerUpdateProfileForm, WithdrawForm, DocumentationCreateForm, \
    DocumentationMediaForm, DocumentationForm, ScheduleForm, JobsForm, NeedcourseForm, OrganizationsForm, \
    ContactPageForm, FaqsForm, BlogsForm, PagesForm, SeoForm, NotificationForm, CategorysForm, SchedulestreamForm, \
    ExcelUploadForm
from webmain.models import Seo, Landing, SettingsGlobale, ContactPage, Faqs
from moderation.forms import SignUpWorkerForm, TicketCommentForm, ModerationGroupsForm, SettingsGlobaleForm, \
    ContactPageForm, FaqsForm, PaymentTypeForm
from useraccount.models import Notification, Withdrawal, UserSession, UserSessionBridge, Notificationgroups, Schedule, \
    Bookmark, Profile, Notebook, History
from moderation.models import ModerationGroups, Ticket, DocumentationsModerMedia, DocumentationsModer, TicketComment, \
    TicketCommentMedia
from integration_payment.models import PaymentType
from django.template.loader import render_to_string


# Create your views here.



@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('upload'):
        file = request.FILES['upload']
        save_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file.name)
        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        file_url = f"{settings.MEDIA_URL}uploads/{file.name}"
        return JsonResponse({'url': file_url})

    return JsonResponse({'error': 'Invalid request'}, status=400)

"""Регистрация/Авторизация"""


class CompanyModerationGroups(LoginRequiredMixin, TemplateView):
    template_name = 'moderations/groups.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            seo_data = Seo.objects.get(pagetype=1)
            context['title'] = seo_data.title
            context['description'] = seo_data.description
            context['seo_previev'] = seo_data.previev
            context['seo_title'] = seo_data.meta_title
            context['seo_description'] = seo_data.meta_description
            context['seo_propertytitle'] = seo_data.propertytitle
            context['seo_propertydescription'] = seo_data.propertydescription
        except Seo.DoesNotExist:
            context['seo_previev'] = None
            context['seo_title'] = None
            context['seo_description'] = None
            context['title'] = None
            context['description'] = None
            context['seo_propertytitle'] = None
            context['seo_propertydescription'] = None
        context['groups'] = ModerationGroups.objects.filter(type_option=2)
        return context


@method_decorator(login_required, name='dispatch')
class ModerationGroupsCreateView(CreateView):
    model = ModerationGroups
    form_class = ModerationGroupsForm
    template_name = 'moderations/groups_form.html'
    success_url = reverse_lazy('moderation:groups')
    context_object_name = 'groups'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['users_queryset'] = self.get_users_queryset()
        return kwargs

    def get_users_queryset(self):
        query = self.request.GET.get('q')
        queryset = Profile.objects.filter(type=2).exclude(id=self.request.user.id).order_by('id')
        if query:
            queryset = queryset.filter(username__icontains=query)
        return queryset

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_users'] = Profile.objects.none()  # Пустой QuerySet для новых групп
        context['users'] = self.get_users_queryset()  # Объединенный список пользователей для поиска
        context['update'] = False
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('moderations/htmx/group_user_search.html', context)
            return JsonResponse({'html': html})
        return super().render_to_response(context, **response_kwargs)


@method_decorator(login_required, name='dispatch')
class ModerationGroupsUpdateView(UpdateView):
    model = ModerationGroups
    form_class = ModerationGroupsForm
    template_name = 'moderations/groups_form.html'
    success_url = reverse_lazy('moderation:groups')
    context_object_name = 'groups'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['users_queryset'] = self.get_users_queryset()
        return kwargs

    def get_users_queryset(self):
        query = self.request.GET.get('q')
        group = self.object
        selected_users = group.users.all()

        # Получаем QuerySet для фильтрации пользователей, которые не выбраны
        queryset = Profile.objects.filter(type=2).exclude(id=self.request.user.id)

        if query:
            queryset = queryset.filter(username__icontains=query)
        else:
            queryset = queryset.exclude(id__in=selected_users).order_by('-id')[:20]

        # Объединяем результаты выбранных пользователей и оставшихся пользователей
        selected_users_ids = selected_users.values_list('id', flat=True)
        additional_users = queryset.values_list('id', flat=True)

        combined_queryset = Profile.objects.filter(
            id__in=list(selected_users_ids) + list(additional_users)
        ).distinct()

        return combined_queryset

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.users.set(self.request.POST.getlist('users'))
        form.instance.types = self.request.POST.getlist('types')
        form.instance.save()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.object
        context['selected_users'] = group.users.all()  # Выбранные пользователи
        context['users'] = self.get_users_queryset()  # Объединенный список пользователей для поиска
        context['update'] = True
        context['selected_types'] = list(group.types)
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('moderations/htmx/group_user_search.html', context)
            return JsonResponse({'html': html})
        return super().render_to_response(context, **response_kwargs)


class ModerationGroupsDeleteView(View):

    def post(self, request, group_id):
        group = get_object_or_404(ModerationGroups, pk=group_id)
        group.delete()
        return JsonResponse({'message': 'Группа успешно удалена'}, status=200)


class KnowledgePage(LoginRequiredMixin, ListView):
    model = DocumentationsModer
    template_name = 'moderations/knowelege.html'
    context_object_name = 'knowelege'

    def get_queryset(self):
        # Фильтруем queryset, чтобы показывать только записи с type=1
        queryset = DocumentationsModer.objects.filter(type=1)

        # Фильтр по названию
        search_name = self.request.GET.get('search_name', '')
        if search_name:
            queryset = queryset.filter(name__icontains=search_name)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        knowelege = self.get_queryset()

        # Пагинация
        paginator = Paginator(knowelege, 1)
        page = self.request.GET.get('page')
        try:
            knowelege_list = paginator.page(page)
        except PageNotAnInteger:
            knowelege_list = paginator.page(1)
        except EmptyPage:
            knowelege_list = paginator.page(paginator.num_pages)

        context['knowelege_list'] = knowelege_list
        context['paginator'] = paginator
        context['page_obj'] = knowelege_list
        context['files'] = DocumentationsModerMedia.objects.filter(documentations__in=knowelege_list)

        return context


class NeedcourseList(LoginRequiredMixin, FormView):
    model = Needcourse
    template_name = 'moderations/needcourse.html'
    paginate_by = 10
    form_class = AssumptioncourseForm
    success_url = reverse_lazy('moderation:needcourses')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['needcourses'] = Needcourse.objects.filter(type=1)
        context['form'] = self.get_form()  # Добавляем форму в контекст
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user if self.request.user.is_authenticated else None
        form.save()
        return super().form_valid(form)


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class CourseAssistantsListView(ListView):
    model = CourseAssistents
    template_name = 'moderations/courses/course_assistants_list.html'
    context_object_name = 'assistants'
    paginate_by = 13

    def get_queryset(self):
        self.course = get_object_or_404(Course, id=self.kwargs['course_id'])
        query = self.request.GET.get('q')

        queryset = CourseAssistents.objects.filter(course=self.course)

        if query:
            queryset = queryset.filter(
                Q(author__name__icontains=query) |
                Q(author__username__icontains=query)
            )

        # Добавляем отладочную информацию
        print(f"Query: {query}")
        print(f"Queryset count: {queryset.count()}")
        print(f"SQL query: {queryset.query}")

        return queryset

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('moderations/courses/course_assistants_list_partial.html', context,
                                    request=self.request)
            return HttpResponse(html)
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        context['total_assistants'] = CourseAssistents.objects.filter(course=self.course).count()
        context['search_query'] = self.request.GET.get('q', '')
        return context


class CategoryscourseList(ListView, LoginRequiredMixin):
    template_name = 'moderations/categoryscourses_settings.html'
    model = CategorysCourse
    context_object_name = 'categorys_settings'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categorys = CategorysCourse.objects.all()

        search_name = self.request.GET.get('search_name', '')
        if search_name:
            categorys = categorys.filter(name__icontains=search_name)

        search_category = self.request.GET.get('search_category', '')
        if search_category:
            categorys = categorys.filter(parent__id=search_category)

        # Пагинация
        paginator = Paginator(categorys, 10)  # 20 элементов на страницу
        page = self.request.GET.get('page')
        try:
            categorys_list = paginator.page(page)
        except PageNotAnInteger:
            categorys_list = paginator.page(1)
        except EmptyPage:
            categorys_list = paginator.page(paginator.num_pages)

        context['categoryscourse'] = categorys_list  # Передаем отфильтрованные задачи
        context['paginator'] = paginator
        context['page_obj'] = categorys_list
        return context


class CategoryscourseCreateView(CreateView, LoginRequiredMixin):
    model = CategorysCourse
    form_class = CategorysCourseForm
    template_name = 'moderations/categoryscourses_form.html'
    success_url = reverse_lazy('moderation:categoryscourse')
    context_object_name = 'categorys'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class CategoryscourseUpdateView(UpdateView, LoginRequiredMixin):
    model = CategorysCourse
    form_class = CategorysCourseForm
    template_name = 'moderations/categoryscourses_form.html'
    success_url = reverse_lazy('moderation:categoryscourse')
    context_object_name = 'categorys'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class CategoryscourseDeleteView(View, LoginRequiredMixin):
    success_url = reverse_lazy('moderation:categoryscourse')

    def post(self, request):
        data = json.loads(request.body)
        categorys_ids = data.get('categorys_ids', [])
        if categorys_ids:
            CategorysCourse.objects.filter(id__in=categorys_ids).delete()
        return JsonResponse({'status': 'success', 'redirect': self.success_url})


class CurcesDocPage(LoginRequiredMixin, ListView):
    model = DocumentationsModer
    template_name = 'moderations/knowelege.html'
    context_object_name = 'knowelege'

    def get_queryset(self):
        # Фильтруем queryset, чтобы показывать только записи с type=1
        queryset = DocumentationsModer.objects.filter(type=2)

        # Фильтр по названию
        search_name = self.request.GET.get('search_name', '')
        if search_name:
            queryset = queryset.filter(name__icontains=search_name)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        knowelege = self.get_queryset()

        # Пагинация
        paginator = Paginator(knowelege, 1)
        page = self.request.GET.get('page')
        try:
            knowelege_list = paginator.page(page)
        except PageNotAnInteger:
            knowelege_list = paginator.page(1)
        except EmptyPage:
            knowelege_list = paginator.page(paginator.num_pages)

        context['knowelege_list'] = knowelege_list
        context['paginator'] = paginator
        context['page_obj'] = knowelege_list
        context['files'] = DocumentationsModerMedia.objects.filter(documentations__in=knowelege_list)

        return context


class Documentation(LoginRequiredMixin, TemplateView):
    template_name = 'moderations/documentation.html'
    model = DocumentationsModer
    context_object_name = 'docs_settings'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        docs = DocumentationsModer.objects.all()

        search_name = self.request.GET.get('search_name', '')
        if search_name:
            docs = docs.filter(name__icontains=search_name)

        paginator = Paginator(docs, 10)  # 20 элементов на страницу
        page = self.request.GET.get('page')
        try:
            docs_list = paginator.page(page)
        except PageNotAnInteger:
            docs_list = paginator.page(1)
        except EmptyPage:
            docs_list = paginator.page(paginator.num_pages)

        context['docs_list'] = docs_list  # Передаем отфильтрованные задачи
        context['paginator'] = paginator
        context['page_obj'] = docs_list
        return context


class DocumentationCreateView(LoginRequiredMixin, CreateView):
    model = DocumentationsModer
    form_class = DocumentationCreateForm
    template_name = 'moderations/documentation_create.html'
    context_object_name = 'documentation'

    @transaction.atomic
    def form_valid(self, form):
        # Сохраняем документ
        comment = form.save(commit=False)
        comment.save()

        # Сохраняем загруженные файлы
        files = self.request.FILES.getlist('files')
        for file in files:
            DocumentationsModerMedia.objects.create(documentations=comment, file=file)

        # Редирект на страницу обновления документации
        return redirect(reverse('moderation:docs_update', args=[comment.id]))

    def form_invalid(self, form):
        print(form.errors)  # Для отладки
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


class UploadFileView(View):
    def post(self, request, documentation_id):
        file = request.FILES.get('file')
        documentation = get_object_or_404(DocumentationsModer, id=documentation_id)
        documentation_file = DocumentationsModerMedia.objects.create(file=file, documentations=documentation)

        return JsonResponse({
            'success': True,
            'file': {
                'id': documentation_file.id,
                'url': documentation_file.file.url,
                'name': documentation_file.file.name
            }
        })


class DeleteFileView(View):
    def delete(self, request, file_id):
        file = get_object_or_404(DocumentationsModerMedia, id=file_id)
        file.delete()
        return JsonResponse({'success': True})


class DocumentationUpdateView(UpdateView, LoginRequiredMixin):
    model = DocumentationsModer
    form_class = DocumentationForm
    template_name = 'moderations/documentation_detail.html'
    success_url = reverse_lazy('moderation:documentation')
    context_object_name = 'documentation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        documentation = self.get_object()
        documentation_files = documentation.documentations.all()

        # Пагинация
        paginator = Paginator(documentation_files, 4)  # 10 элементов на страницу
        page = self.request.GET.get('page')
        try:
            files_list = paginator.page(page)
        except PageNotAnInteger:
            files_list = paginator.page(1)
        except EmptyPage:
            files_list = paginator.page(paginator.num_pages)

        context['documentation_files'] = files_list  # Передаем отфильтрованные файлы
        context['paginator'] = paginator
        context['page_obj'] = files_list
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class DocumentationDeleteView(LoginRequiredMixin, View):
    success_url = reverse_lazy('moderation:documentation')

    def post(self, request):
        data = json.loads(request.body)
        docs_ids = data.get('docs_ids', [])
        if docs_ids:
            DocumentationsModer.objects.filter(id__in=docs_ids).delete()
        return JsonResponse({'status': 'success', 'redirect': self.success_url})


"""Регистрация/Авторизация"""




@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class TeacherListView(ListView):
    model = Profile
    template_name = 'moderations/teacher_list.html'
    context_object_name = 'users'
    paginate_by = 13

    def get_queryset(self):
        query = self.request.GET.get('q')

        # Подзапрос для подсчета курсов
        course_count = Course.objects.filter(author=OuterRef('pk')).values('author').annotate(count=Count('pk')).values(
            'count')

        # Подзапрос для подсчета отзывов
        review_count = Courserewievs.objects.filter(course__author=OuterRef('pk')).values('course__author').annotate(
            count=Count('pk')).values('count')

        # Подзапрос для подсчета оплаченных курсов
        paid_course_count = Courseuser.objects.filter(
            course__author=OuterRef('pk'),
            status=2  # Статус "Оплачено"
        ).values('course__author').annotate(count=Count('pk', distinct=True)).values('count')

        queryset = Profile.objects.filter(type=1).exclude(id=self.request.user.id).annotate(
            course_count=Subquery(course_count),
            review_count=Subquery(review_count),
            paid_course_count=Subquery(paid_course_count)
        ).order_by('id')

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(username__icontains=query)
            )

        # Добавляем отладочную информацию
        print(f"Query: {query}")
        print(f"Queryset count: {queryset.count()}")
        print(f"SQL query: {queryset.query}")

        return queryset

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('moderations/teacher_list_partial.html', context, request=self.request)
            return HttpResponse(html)
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = Profile.objects.filter(type=1).count()
        context['search_query'] = self.request.GET.get('q', '')
        return context


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class CertificateListView(ListView):
    model = Coursesertificateuser
    template_name = 'moderations/certificate_list.html'
    context_object_name = 'coursecertificates'
    paginate_by = 13

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        certificates = Coursesertificateuser.objects.filter(user_id=user.id)
        context['certificates'] = certificates
        context['coursecertificate'] = [cert.course for cert in certificates]
        return context

# Курсы


class CoursesertificateuserListView(LoginRequiredMixin, ListView):
    model = Coursesertificateuser
    template_name = 'moderations/courses/coursesertificateuser.html'  # Замените на путь к вашему шаблону
    context_object_name = 'coursesertificateuser'
    paginate_by = 10  # Количество уведомлений на странице

    def get_queryset(self):
        # Получаем все уведомления пользователя
        queryset = Coursesertificateuser.objects.filter(user=self.request.user)

        return queryset


class CoursePaymentView(View):
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        user = request.user
        profile = get_object_or_404(Profile, id=user.id)

        # Приведение баланса к числовому типу
        try:
            current_balance = int(profile.balance)
        except ValueError:
            messages.error(request, 'Ошибка: неверное значение баланса.')
            return redirect('moderation:courses')

        # Проверка баланса пользователя
        if current_balance >= course.price:
            # Обновление баланса пользователя
            profile.balance = str(current_balance - course.price)
            profile.save()

            # Добавление пользователя в участники курса
            course.participants.add(user)
            course.save()

            # Проверка или создание Courseuser
            courseuser, created = Courseuser.objects.get_or_create(
                user=user,
                course=course,
                defaults={
                    'status': 2,  # Оплачено
                    'type': 1,    # Проходит
                }
            )

            if not created:
                # Обновление существующей записи
                courseuser.status = 2
                courseuser.type = 1
                courseuser.save()

            messages.success(request, 'Оплата прошла успешно. Вы добавлены в участники курса.')
        else:
            messages.error(request, 'Недостаточно средств на балансе для оплаты курса.')

        return redirect('moderation:coursepassing', course_id=course.id)

class StartFreeCourseView(View):
    def get(self, request, course_id):
        """
        Логика начала прохождения бесплатного курса.
        Создает запись в модели Courseuser, если ее нет.
        """
        course = get_object_or_404(Course, id=course_id)

        # Проверяем, что курс бесплатный
        if course.price <= 0:
            # Создаем запись в Courseuser, если ее нет
            courseuser, created = Courseuser.objects.get_or_create(
                user=request.user,
                course=course,
                defaults={
                    'status': 2,  # Оплачено
                    'type': 1,    # Проходит
                    'create': timezone.now(),  # Текущая дата и время
                }
            )
            # Перенаправляем на страницу прохождения курса
            return redirect('moderation:coursepassing', course_id=course.id)

        # Если курс не бесплатный, перенаправляем на страницу списка курсов
        return redirect('courses:list')

class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'moderations/courses/courses.html'
    context_object_name = 'courses'
    paginate_by = 10

    PAYMENT_NOT_PASSED = 1
    PAYMENT_PASSED = 2

    def get_queryset(self):
        user = self.request.user
        course_content_type = ContentType.objects.get_for_model(Course)
        self.course_content_type = course_content_type

        queryset = Course.objects.filter(draft=False)

        # Фильтрация по username автора курса
        username = self.request.GET.get('username')
        if username:
            queryset = queryset.filter(author__username__icontains=username)

        queryset = queryset.annotate(
            has_courseuser=Exists(
                Courseuser.objects.filter(
                    user=user,
                    course=OuterRef('pk'),
                    status=self.PAYMENT_PASSED
                )
            ),
            is_bookmarked=Exists(
                Bookmark.objects.filter(
                    user=user,
                    content_type=course_content_type,
                    object_id=OuterRef('pk')
                )
            )
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_courses'] = Courseuser.objects.filter(
            user=self.request.user,
            status=self.PAYMENT_PASSED
        ).values_list('course_id', flat=True)
        context['course_content_type_id'] = self.course_content_type.id

        # Добавляем текущее значение фильтра по username
        context['username_filter'] = self.request.GET.get('username', '')

        # SEO-параметры
        context['seo_title'] = "Курсы"
        context['seo_description'] = "Список доступных курсов"
        context['seo_previev'] = None
        context['seo_propertytitle'] = "Страница Курсов"
        context['seo_propertydescription'] = "Курсы для обучения"

        return context


class CourseAvailableListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'moderations/courses/coursesavailable.html'
    context_object_name = 'courses'
    paginate_by = 10

    PAYMENT_NOT_PASSED = 1
    PAYMENT_PASSED = 2

    def get_queryset(self):
        user = self.request.user
        course_content_type = ContentType.objects.get_for_model(Course)
        self.course_content_type = course_content_type

        queryset = Course.objects.filter(draft=False)

        # Фильтрация по username автора курса
        username = self.request.GET.get('username')
        if username:
            queryset = queryset.filter(author__username__icontains=username)

        queryset = queryset.annotate(
            has_courseuser=Exists(
                Courseuser.objects.filter(
                    user=user,
                    course=OuterRef('pk'),
                    status=self.PAYMENT_PASSED
                )
            ),
            is_bookmarked=Exists(
                Bookmark.objects.filter(
                    user=user,
                    content_type=course_content_type,
                    object_id=OuterRef('pk')
                )
            )
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_courses'] = Courseuser.objects.filter(
            user=self.request.user,
            status=self.PAYMENT_PASSED
        ).values_list('course_id', flat=True)
        context['course_content_type_id'] = self.course_content_type.id

        # Добавляем текущее значение фильтра по username
        context['username_filter'] = self.request.GET.get('username', '')

        # SEO-параметры
        context['seo_title'] = "Курсы"
        context['seo_description'] = "Список доступных курсов"
        context['seo_previev'] = None
        context['seo_propertytitle'] = "Страница Курсов"
        context['seo_propertydescription'] = "Курсы для обучения"

        return context


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'moderations/courses/course.html'  # Замените на путь к вашему шаблону
    context_object_name = 'course'
    slug_field = "slug"

    PAYMENT_NOT_PASSED = 1
    PAYMENT_PASSED = 2

    def get_queryset(self):
        user = self.request.user
        course_content_type = ContentType.objects.get_for_model(Course)
        self.course_content_type = course_content_type

        queryset = Course.objects.filter(draft=False)

        # Фильтрация по username автора курса
        username = self.request.GET.get('username')
        if username:
            queryset = queryset.filter(author__username__icontains=username)

        queryset = queryset.annotate(
            has_courseuser=Exists(
                Courseuser.objects.filter(
                    user=user,
                    course=OuterRef('pk'),
                    status=self.PAYMENT_PASSED
                )
            ),
            is_bookmarked=Exists(
                Bookmark.objects.filter(
                    user=user,
                    content_type=course_content_type,
                    object_id=OuterRef('pk')
                )
            )
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем текущий курс
        course = self.get_object()

        # Получаем модули с темами, используя prefetch_related
        modules = Modules.objects.filter(course=course).order_by('position')
        modules_with_themes = modules.prefetch_related(
            Prefetch('modulescourse', queryset=Themes.objects.order_by('position'), to_attr='themes_list')
        )

        # Получаем темы, не привязанные к модулям
        themes_without_module = Themes.objects.filter(course=course, modules__isnull=True).order_by('position')

        # Добавляем данные в контекст
        context['user_courses'] = Courseuser.objects.filter(
            user=self.request.user,
            status=self.PAYMENT_PASSED
        ).values_list('course_id', flat=True)

        if self.request.user.is_authenticated:
            content_type = ContentType.objects.get_for_model(course)
            user = self.request.user

            # Проверяем, существует ли запись за сегодня
            today = now().date()
            history_exists = History.objects.filter(
                user=user,
                content_type=content_type,
                object_id=course.id,
                created_at__date=today
            ).exists()

            if not history_exists:
                History.objects.create(
                    user=user,
                    content_type=content_type,
                    object_id=course.id
                )
                course.pageviews += 1
                course.save()

        # Передаем mодули с темами и темы без модулей
        context['modules_with_themes'] = modules_with_themes
        context['themes_without_module'] = themes_without_module
        context['course_content_type_id'] = self.course_content_type.id

        # Добавляем текущее значение фильтра по username
        context['username_filter'] = self.request.GET.get('username', '')
        # Добавляем категорию курса
        context['all_categories'] = CategorysCourse.objects.all()

        # Передаем course_content_type_id в контекст
        context['course_content_type_id'] = self.course_content_type.id

        return context


class CoursePassingDetailView(DetailView):
    model = Course
    template_name = 'moderations/courses/coursepassingdetail.html'
    context_object_name = 'course'

    PAYMENT_NOT_PASSED = 1
    PAYMENT_PASSED = 2

    def dispatch(self, request, *args, **kwargs):
        course_id = self.kwargs.get('course_id')
        user = request.user
        course = Course.objects.get(pk=course_id)
        # Проверяем, есть ли у пользователя запись в Courseuser для текущего курса
        course_user = Courseuser.objects.filter(user=user, course_id=course_id).first()
        if not course_user and course.price != 0:
            # Если нет записи, перенаправляем на страницу со списком курсов
            return redirect('moderation:courses')

        # Если запись существует, продолжаем обработку запроса
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        course_content_type = ContentType.objects.get_for_model(Course)

        queryset = Course.objects.filter(draft=False).annotate(
            has_courseuser=Exists(
                Courseuser.objects.filter(
                    user=user,
                    course=OuterRef('pk'),
                    status=self.PAYMENT_PASSED
                )
            ),
            is_bookmarked=Exists(
                Bookmark.objects.filter(
                    user=user,
                    content_type=course_content_type,
                    object_id=OuterRef('pk')
                )
            )
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        user = self.request.user

        # Получаем ContentType для модели Course
        course_content_type = ContentType.objects.get_for_model(Course)

        # Получаем модули и темы курса с их отношениями в одном запросе
        modules_with_themes = Modules.objects.filter(course=course).order_by('position').prefetch_related(
            Prefetch('modulescourse', queryset=Themes.objects.order_by('position'), to_attr='themes_list')
        )

        # Получаем курсы пользователя, где статус "Оплачено"
        user_courses = Courseuser.objects.filter(
            user=user,
            status=self.PAYMENT_PASSED
        ).values_list('course_id', flat=True)

        # Получаем все темы без привязки к модулю
        themes_without_module = Themes.objects.filter(course=course, modules__isnull=True).order_by('position')

        # Получаем доступные темы и отслеживаем статус прохождения
        accessible_themes = []
        last_completed_theme_position = 0  # Переменная для отслеживания последней пройденной темы
        all_themes_completed = True  # Переменная для проверки, прошел ли пользователь все темы

        # Используем предварительно загруженные темы для быстрого доступа
        for module in modules_with_themes:
            for theme in module.themes_list:
                # Проверяем доступность темы
                if theme.access_type:  # Если лекция доступна только после прохождения предыдущей
                    if theme.position == last_completed_theme_position + 1:
                        # Проверка прохождения теста
                        passed = ThemesQuestion.objects.filter(
                            user=user,
                            themes=theme,
                            status=1  # Статус "Прошел"
                        ).exists()

                        if passed:
                            accessible_themes.append(theme)
                            last_completed_theme_position = theme.position  # Обновляем последнюю пройденную тему
                        else:
                            all_themes_completed = False
                    else:
                        accessible_themes.append(theme)
                else:
                    accessible_themes.append(theme)

                if theme.home_work_status:
                    theme.home_work_data = {
                        'home_work': theme.home_work,
                        'home_work_status': theme.home_work_status
                    }
                else:
                    theme.home_work_data = None
                # Проверка, был ли пройден тест для темы
                if not ThemesQuestion.objects.filter(
                        user=user,
                        themes=theme,
                        status=1  # Статус "Прошел"
                ).exists():
                    all_themes_completed = False

        if self.request.user.is_authenticated:
            content_type = ContentType.objects.get_for_model(course)
            user = self.request.user

            # Проверяем, существует ли запись за сегодня
            today = now().date()
            history_exists = History.objects.filter(
                user=user,
                content_type=content_type,
                object_id=course.id,
                created_at__date=today
            ).exists()

            if not history_exists:
                History.objects.create(
                    user=user,
                    content_type=content_type,
                    object_id=course.id
                )
                course.pageviews += 1
                course.save()

        # Добавляем в контекст
        context['user_courses'] = user_courses
        context['modules_with_themes'] = modules_with_themes
        context['themes_without_module'] = themes_without_module
        context['all_categories'] = CategorysCourse.objects.all()
        context['course_content_type_id'] = course_content_type.id
        context['accessible_themes'] = accessible_themes
        context['all_themes_completed'] = all_themes_completed  # Флаг для проверки, все ли темы пройдены

        return context

    def get_object(self, queryset=None):
        course_id = self.kwargs.get('course_id')
        return get_object_or_404(Course, id=course_id)

class SubmitHomeWorkView(View):
    def post(self, request):
        user = request.user
        theme_id = request.POST.get('theme_id')
        text = request.POST.get('text')
        files = request.FILES.getlist('files')

        theme = get_object_or_404(Themes, id=theme_id)

        try:
            # Создаем запись о домашнем задании
            homework = HomeWork.objects.create(
                user=user,
                theme=theme,
                text=text
            )

            # Сохраняем файлы
            for file in files:
                # Определяем тип файла на основе расширения
                _, extension = os.path.splitext(file.name.lower())

                if extension in ['.mp4', '.avi', '.mov', '.wmv']:
                    file_type = 1  # Видео
                elif extension in ['.mp3', '.wav', '.ogg', '.flac']:
                    file_type = 2  # Аудио
                else:
                    file_type = 3  # Документ

                HomeWorkFiles.objects.create(
                    homework=homework,
                    file=file,
                    type=file_type,
                    name=file.name  # Можно передать имя файла, если необходимо
                )

            return JsonResponse({'success': True})

        except Exception as e:
            print(e)
            return JsonResponse({'success': False, 'error': str(e)})

def get_theme_description(request, theme_id):
    try:
        theme = Themes.objects.get(id=theme_id)
    except Themes.DoesNotExist:
        return JsonResponse({'error': 'Тема не найдена'}, status=404)

    files = theme.themes_file.all()

    questions = False
    if Qwiz.objects.filter(themes=theme).exists():
        questions = True

    # Получаем самую последнюю запись ThemesQuestion для пользователя и текущей темы
    user_status = ThemesQuestion.objects.filter(user=request.user, themes=theme).order_by('-data').first()

    # Флаг и время для управления кнопкой и таймером
    is_test_accessible = True
    time_remaining = None
    test_completed = False
    # Проверка, что статус == 3 (не сдал) и attempts_status == True
    if user_status and user_status.status == 3 and theme.attempts_status:
        is_test_accessible = False

        # Если у пользователя есть запись, проверим время
        time_started = user_status.last_attempt_time  # Время последней попытки
        time_limit = timezone.timedelta(minutes=theme.attempts)  # Время, отведенное на тест
        time_elapsed = timezone.now() - time_started  # Время, прошедшее с последней попытки

        # Если время истекло
        if time_elapsed >= time_limit:
            # Сбросить состояние, если время истекло
            user_status.status = 2  # Статус на "сдал"
            user_status.save()
            time_remaining = 0
        else:
            # Оставшееся время
            time_remaining = (time_limit - time_elapsed).seconds  # Время в секундах

    if user_status and user_status.status == 1:
        test_completed = True

    # Если нет записи или статус не 3, то кнопка доступна
    files_data = []
    for file in files:
        file_data = {
            'id': file.id,
            'type': file.type,
            'name': file.name,
            'content': file.content,
            'files': file.files.url if file.files else None
        }
        files_data.append(file_data)

    # Добавление информации о домашнем задании
    home_work_status = theme.home_work_status  # Проверка наличия текста домашнего задания
    home_work = theme.home_work if home_work_status else None

    # Ответ с описанием, файлами, доступностью теста и оставшимся временем
    return JsonResponse({
        'description': theme.description,
        'files': files_data,
        'is_test_accessible': is_test_accessible,
        'time_remaining': time_remaining,
        'test_completed': test_completed,
        'home_work_status': home_work_status,
        'home_work': home_work,
        'have_questions': questions,
    })
class QuizPassView(TemplateView):
    template_name = 'moderations/courses/quiz_passing.html'  # Название шаблона

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        theme_id = self.kwargs.get('theme_id')
        theme = get_object_or_404(Themes, id=theme_id)
        quizzes = Qwiz.objects.filter(themes=theme)
        quizzes_six = Qwiz.objects.filter(themes=theme,type=6)

        test_duration = theme.test_duration

        # Словарь для хранения вопросов по викторинам
        quizzes_with_matching_questions = {}

        for quiz in quizzes_six:
            # Получаем все вопросы типа 6 (Выберите соответствие) для текущей викторины
            matching_questions = Question.objects.filter(qwiz=quiz, qwiz__type=6)

            # Списки для левых и правых элементов
            left_items = []
            right_items = []

            # Формируем списки элементов для всех вопросов
            for question in matching_questions:
                if question.left_text:
                    left_items.append({'type': 'text', 'content': question.left_text, 'question_id': question.id})
                if question.left_file:
                    left_items.append({'type': 'file', 'content': question.left_file.url, 'question_id': question.id})

                if question.right_text:
                    right_items.append({'type': 'text', 'content': question.right_text, 'question_id': question.id})
                if question.right_file:
                    right_items.append({'type': 'file', 'content': question.right_file.url, 'question_id': question.id})

            # Перемешиваем левые и правые элементы независимо
            random.shuffle(left_items)
            random.shuffle(right_items)

            # Убедимся, что количество элементов совпадает
            min_length = min(len(left_items), len(right_items))
            left_items = left_items[:min_length]
            right_items = right_items[:min_length]

            # Создаем список вопросов с произвольно сопоставленными левой и правой частями
            shuffled_questions = []
            for left, right in zip(left_items, right_items):
                shuffled_questions.append({
                    'left': left,
                    'right': right,
                    'left_question_id': left['question_id'],  # ID левой части
                    'right_question_id': right['question_id']  # ID правой части
                })

            # Добавляем вопросы в словарь по имени викторины
            quizzes_with_matching_questions[quiz.name] = shuffled_questions

        # Добавляем в контекст
        context['theme'] = theme
        context['quizzes'] = quizzes
        context['test_duration'] = test_duration
        context['total_questions'] = quizzes.count()
        context['quizzes_with_matching_questions'] = quizzes_with_matching_questions

        return context

    def is_valid_connection(self, question, left_id, right_id):
        """
        Проверяет, является ли соединение корректным, сравнивая числовые части идентификаторов
        и проверяя, что соединение соответствует ожидаемым правилам.

        Ожидается, что идентификаторы имеют формат:
          left_id  -> "left-<question_id>-<тип>"
          right_id -> "right-<question_id>-<тип>"
        """
        # Разделяем идентификаторы по символу '-'
        left_parts = left_id.split('-')
        right_parts = right_id.split('-')

        print(f"left_parts: {left_parts}")
        print(f"right_parts: {right_parts}")

        # Если формат идентификатора нарушен, возвращаем False
        if len(left_parts) < 3 or len(right_parts) < 3:
            return False

        # Проверяем, что числовой идентификатор совпадает у обеих частей и совпадает с question.id
        if left_parts[1] != right_parts[1] or left_parts[1] != str(question.id):
            return False

        # Проверяем, что соединение соответствует ожидаемым правилам
        # Например, если left_parts[2] == 'file', то right_parts[2] должен быть 'text'
        if left_parts[2] == 'file' and right_parts[2] == 'text':
            return True
        elif left_parts[2] == 'text' and right_parts[2] == 'file':
            return True

        # Если соединение не соответствует правилам, возвращаем False
        return False

    def post(self, request, *args, **kwargs):
        # Получаем текущую тему
        theme_id = self.kwargs.get('theme_id')
        theme = get_object_or_404(Themes, id=theme_id)

        # Получаем все тесты, связанные с темой
        quizzes = Qwiz.objects.filter(themes=theme)

        # Собираем ответы пользователя из формы
        user_answers = {}
        qwiz_text = []  # Для формирования текста
        points = 0
        correct_answers = 0
        processed_quizzes = set()

        for quiz in quizzes:
            # Проверяем, был ли уже обработан этот квиз
            if quiz.id in processed_quizzes:
                continue  # Пропускаем, если квиз уже был обработан

            if quiz.type == 6:
                connections_data = request.POST.get('connections')
                print('connections_data----------------', connections_data)

                if connections_data:
                    import json
                    try:
                        # Парсим JSON с информацией о соединениях
                        connections = json.loads(connections_data)
                    except json.JSONDecodeError:
                        connections = []

                    # Получаем все вопросы, относящиеся к данному quiz
                    questions = quiz.question_quiz.all()
                    all_questions_correct = True  # Флаг, указывающий, что все вопросы отвечены правильно
                    question_texts = []

                    for question in questions:
                        question_id = str(question.id)
                        # Фильтруем соединения, относящиеся к текущему вопросу, по началу идентификаторов
                        question_connections = [
                            conn for conn in connections
                            if conn.get('leftId', '').startswith(f"left-{question_id}-") and
                               conn.get('rightId', '').startswith(f"right-{question_id}-")
                        ]

                        if question_connections:
                            is_correct = True  # Флаг корректности соединений для текущего вопроса
                            for connection in question_connections:
                                left_id = connection.get('leftId', '')
                                right_id = connection.get('rightId', '')
                                # Используем проверку соединения
                                if not self.is_valid_connection(question, left_id, right_id):
                                    is_correct = False
                                    break

                            if is_correct:
                                question_texts.append(f"question: {question_id}, point: {quiz.point}")
                            else:
                                question_texts.append(f"question: {question_id}, point: 0")
                                all_questions_correct = False  # Хотя бы один вопрос отвечен неправильно
                        else:
                            question_texts.append(f"question: {question_id}, point: 0")
                            all_questions_correct = False  # Нет соединений для вопроса

                    # Если все вопросы отвечены правильно, добавляем баллы за квиз
                    if all_questions_correct:
                        points += quiz.point
                        correct_answers += 1
                        qwiz_text.append(
                            f"qwiz: {quiz.id}, questions: {', '.join(question_texts)}, total points: {quiz.point}")
                    else:
                        qwiz_text.append(f"qwiz: {quiz.id}, questions: {', '.join(question_texts)}, total points: 0")
                else:
                    qwiz_text.append(f"qwiz: {quiz.id}, questions: No connections provided, total points: 0")

                # Добавляем квиз в обработанные
                processed_quizzes.add(quiz.id)

            # Обработка для type == 5
            elif quiz.type == 5:
                for question in quiz.question_quiz.all():
                    answer = request.POST.get(f"question_{question.id}")
                    user_answers[question.id] = answer
                    print(quiz.point, 'POINT----------------')

                    string_answer = request.POST.get(f"answer_{question.id}")
                    description = question.description
                    strong_pattern = re.compile(r'<strong>(.*?)</strong>')  # Шаблон для <strong>
                    strong_texts = [text.strip() for text in strong_pattern.findall(description)]

                    if string_answer:
                        for strong_text in strong_texts:
                            if string_answer.strip().lower() == strong_text.strip().lower():
                                correct_answers += 1
                                point = quiz.point
                                points += quiz.point  # Правильный ответ
                                qwiz_text.append(f"qwiz: {quiz.id}, question: {question.id}, point: {point}")
                                break
                        else:
                            qwiz_text.append(f"qwiz: {quiz.id}, question: {question.id}, point: 0")

            # Обработка для type == 4
            elif quiz.type == 4:
                # Собираем все вопросы для текущего квиза
                questions = quiz.question_quiz.all()

                # Логируем ответы для всех вопросов в квизе
                provided_answers = {
                    question.id: request.POST.get(f"answer_{question.id}")
                    for question in questions
                }

                print(f"Ответы для квиза {quiz.id}, вопросы: {provided_answers}")  # Логгируем все ответы для квиза

                # Проверяем, что все ответы предоставлены
                if len(provided_answers) == questions.count() and all(provided_answers.values()):
                    correct = True
                    question_ids = []

                    # Проверяем правильность ответа для каждого вопроса
                    for question in questions:
                        selected_answer = provided_answers[question.id]
                        print(f"Ответ для вопроса {question.id}: {selected_answer}")  # Логгируем ответ на каждый вопрос
                        question_ids.append(str(question.id))  # Сохраняем ID вопроса

                        # Проверяем правильность ответа
                        if not (
                                (question.right_answer == 1 and selected_answer == question.title) or
                                (question.right_answer == 2 and selected_answer == question.second_title)
                        ):
                            correct = False  # Если хотя бы один ответ неверный
                            print(f"Ответ для вопроса {question.id} неверный")  # Логгируем неверный ответ

                    # Формируем строку и начисляем баллы, если все ответы корректны
                    if correct:
                        print(
                            f"Все ответы верны для квиза {quiz.id}, начисляем {quiz.point} баллов.")  # Логгируем начисление баллов
                        correct_answers += 1
                        points += quiz.point  # Баллы за весь quiz
                        qwiz_text.append(f"qwiz: {quiz.id}, questions: {', '.join(question_ids)}, point: {quiz.point}")
                    else:
                        print(
                            f"Некоторые ответы неверны для квиза {quiz.id}, баллы 0.")  # Логгируем, если есть неверные ответы
                        qwiz_text.append(f"qwiz: {quiz.id}, questions: {', '.join(question_ids)}, point: 0")

                else:
                    print(f"Не все ответы предоставлены для квиза {quiz.id}. Пропускаем.")

            # Логика для других типов тестов
            else:
                processed_quizzes = set()  # Множество для отслеживания обработанных квизов
                quiz_points = 0  # Переменная для хранения баллов за текущий квиз
                correct_answers_for_quiz = 0  # Счетчик правильных ответов в квизе
                question_ids = []  # Список ID вопросов в текущем квизе

                for question in quiz.question_quiz.all():
                    # Получаем ответ пользователя из POST-запроса
                    answer = request.POST.get(f"question_{question.id}")
                    user_answers[question.id] = answer

                    # Проверяем ответ на корректность
                    if answer and question.right_answer == 2:
                        correct_answers_for_quiz += 1
                        quiz_points = quiz.point  # Начисляем баллы только один раз за весь квиз
                    elif answer:
                        correct_answers_for_quiz += 0  # Ответ неверный, баллы не начисляем

                    # Сохраняем ID вопроса для формирования строки
                    question_ids.append(str(question.id))

                # Если квиз еще не обработан, добавляем его в результат
                if quiz.id not in processed_quizzes:
                    processed_quizzes.add(quiz.id)  # Добавляем квиз в множество обработанных
                    qwiz_text.append(
                        f"qwiz: {quiz.id}, questions: {', '.join(question_ids)}, point: {quiz_points} ,qwiz name {quiz.name}"
                    )
                    correct_answers += 1
                    points += quiz_points  # Добавляем баллы за квиз только один раз

                # Добавляем текущий квиз в обработанные
                processed_quizzes.add(quiz.id)

            # Добавляем квиз в обработанные, чтобы избежать повторной обработки
            processed_quizzes.add(quiz.id)
        # Формируем строку для поля qwiz
        print("\n".join(qwiz_text))
        print(f"Total points: {points}, Correct answers: {correct_answers}")

        qwiz_string = "\n".join(qwiz_text)

        if quizzes.count() != 0 :
            if theme.point_status:
                # Создаем запись в модели ThemesQuestion
                ThemesQuestion.objects.create(
                    user=request.user,
                    themes=theme,
                    qwiz=qwiz_string,
                    data=timezone.now(),
                    point=points,
                    correctanswer=correct_answers,
                    status=1 if points >= theme.point else 3  # Статус: 1 - прошел, 3 - не прошел
                )
            else:
                ThemesQuestion.objects.create(
                    user=request.user,
                    themes=theme,
                    qwiz=qwiz_string,
                    data=timezone.now(),
                    point=points,
                    correctanswer=correct_answers,
                    status=1  # Статус: 1 - прошел, 3 - не прошел
                )
        else:
            ThemesQuestion.objects.create(
                user=request.user,
                themes=theme,
                qwiz=qwiz_string,
                data=timezone.now(),
                point=points,
                correctanswer=correct_answers,
                status=1
            )

        # Перенаправляем на страницу с результатами
        return redirect('moderation:quiz_completed', theme_id=theme.id)



@login_required
def download_certificate(request, course_id):
    """
    Вьюха для создания и скачивания сертификата для пользователя по курсу.
    """
    # Получаем объект курса
    course = get_object_or_404(Course, id=course_id)

    # Получаем первый сертификат для курса
    certificate = get_object_or_404(Coursesertificate, course=course)

    # Проверяем, существует ли сертификат для этого пользователя
    certificate_user, created = Coursesertificateuser.objects.get_or_create(course=certificate, user=request.user)

    # 'created' будет True, если объект был создан, и False, если он уже существовал
    if created:
        # Логика, которая выполняется только при создании нового объекта
        print(f"Сертификат для пользователя {request.user} был успешно создан.")
        # Можно добавить дополнительные действия, например, генерацию сертификата, если нужно.
        # Например, создание сертификата как файл или отправка его в модель.

    # После того как сертификат был либо создан, либо уже существует, отправляем файл для скачивания
    if certificate_user.certificate:
        return FileResponse(certificate_user.certificate.open(), as_attachment=True,
                            filename=certificate_user.certificate.name.split('/')[-1])
    else:
        raise Http404("Сертификат не найден.")

class CourseReviewsView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'moderations/courses/course_reviews.html'
    context_object_name = 'course'
    slug_field = "slug"

    PAYMENT_NOT_PASSED = 1
    PAYMENT_PASSED = 2

    COMMENTS_PER_PAGE = 4

    def get_queryset(self):
        user = self.request.user
        course_content_type = ContentType.objects.get_for_model(Course)
        self.course_content_type = course_content_type

        queryset = Course.objects.filter(draft=False).annotate(
            has_courseuser=Exists(
                Courseuser.objects.filter(
                    user=user,
                    course=OuterRef('pk'),
                    status=self.PAYMENT_PASSED
                )
            ),
            is_bookmarked=Exists(
                Bookmark.objects.filter(
                    user=user,
                    content_type=course_content_type,
                    object_id=OuterRef('pk')
                )
            )
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user

        rewievs_list = Courserewievs.objects.filter(course=course).order_by('create')
        paginator = Paginator(rewievs_list, self.COMMENTS_PER_PAGE)

        page = self.request.GET.get('page')
        try:
            page_number = int(page)
        except (TypeError, ValueError):
            page_number = 1

        try:
            rewievs = paginator.page(page_number)
        except EmptyPage:
            # Если страница пуста, возвращаем последнюю страницу
            rewievs = paginator.page(paginator.num_pages)

        context['rewievs'] = rewievs

        context['user_courses'] = Courseuser.objects.filter(
            user=self.request.user,
            status=self.PAYMENT_PASSED
        ).values_list('course_id', flat=True)

        context['has_review'] = Courserewievs.objects.filter(course=course, user=user).exists()
        context['course_content_type_id'] = self.course_content_type.id

        return context


class CourseCommentView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'moderations/courses/course_comments.html'
    context_object_name = 'course'
    slug_field = "slug"

    PAYMENT_NOT_PASSED = 1
    PAYMENT_PASSED = 2

    COMMENTS_PER_PAGE = 4

    def get_queryset(self):
        user = self.request.user
        course_content_type = ContentType.objects.get_for_model(Course)
        self.course_content_type = course_content_type

        queryset = Course.objects.filter(draft=False).annotate(
            has_courseuser=Exists(
                Courseuser.objects.filter(
                    user=user,
                    course=OuterRef('pk'),
                    status=self.PAYMENT_PASSED
                )
            ),
            is_bookmarked=Exists(
                Bookmark.objects.filter(
                    user=user,
                    content_type=course_content_type,
                    object_id=OuterRef('pk')
                )
            )
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user

        comments_list = Coursecomments.objects.filter(course=course).order_by('parent', 'create')

        paginator = Paginator(comments_list, self.COMMENTS_PER_PAGE)

        page = self.request.GET.get('page')
        try:
            page_number = int(page)
        except (TypeError, ValueError):
            page_number = 1

        try:
            comments = paginator.page(page_number)
        except EmptyPage:
            # Если страница пуста, возвращаем последнюю страницу
            comments = paginator.page(paginator.num_pages)

        context['comments'] = comments
        context['total_comments'] = comments_list.count()

        context['user_courses'] = Courseuser.objects.filter(
            user=user,
            status=self.PAYMENT_PASSED
        ).values_list('course_id', flat=True)

        context['course_content_type_id'] = self.course_content_type.id

        return context


class MyCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'moderations/courses/mycourses.html'  # Замените на путь к вашему шаблону
    context_object_name = 'courses'
    paginate_by = 10  # Количество уведомлений на странице

    def get_queryset(self):
        # Получаем все уведомления пользователя
        queryset = Course.objects.filter(author=self.request.user)

        return queryset


class MyCourseCommentView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'moderations/courses/mycourse_comments.html'
    context_object_name = 'course'
    slug_field = "pk"

    PAYMENT_NOT_PASSED = 1
    PAYMENT_PASSED = 2

    COMMENTS_PER_PAGE = 4

    def get_queryset(self):
        user = self.request.user
        course_content_type = ContentType.objects.get_for_model(Course)
        self.course_content_type = course_content_type

        queryset = Course.objects.filter(draft=False).annotate(
            has_courseuser=Exists(
                Courseuser.objects.filter(
                    user=user,
                    course=OuterRef('pk'),
                    status=self.PAYMENT_PASSED
                )
            ),
            is_bookmarked=Exists(
                Bookmark.objects.filter(
                    user=user,
                    content_type=course_content_type,
                    object_id=OuterRef('pk')
                )
            )
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user

        comments_list = Coursecomments.objects.filter(course=course).order_by('parent', 'create')

        paginator = Paginator(comments_list, self.COMMENTS_PER_PAGE)

        page = self.request.GET.get('page')
        try:
            page_number = int(page)
        except (TypeError, ValueError):
            page_number = 1

        try:
            comments = paginator.page(page_number)
        except EmptyPage:
            # Если страница пуста, возвращаем последнюю страницу
            comments = paginator.page(paginator.num_pages)

        context['comments'] = comments
        context['total_comments'] = comments_list.count()

        context['user_courses'] = Courseuser.objects.filter(
            user=user,
            status=self.PAYMENT_PASSED
        ).values_list('course_id', flat=True)

        context['course_content_type_id'] = self.course_content_type.id

        return context


class DeleteCourseCommentView(LoginRequiredMixin, View):
    def post(self, request, comment_id):
        comment = get_object_or_404(Coursecomments, id=comment_id)

        if request.user.is_staff or request.user == comment.user:
            try:
                comment.delete()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Комментарий успешно удален.'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Ошибка при удалении комментария: {str(e)}'
                }, status=400)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'У вас нет прав для удаления этого комментария.'
            }, status=403)


class MyCourseReviewsView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'moderations/courses/mycourse_reviews.html'
    context_object_name = 'course'
    slug_field = "slug"

    PAYMENT_NOT_PASSED = 1
    PAYMENT_PASSED = 2

    COMMENTS_PER_PAGE = 4

    def get_queryset(self):
        user = self.request.user
        course_content_type = ContentType.objects.get_for_model(Course)
        self.course_content_type = course_content_type

        queryset = Course.objects.filter(draft=False).annotate(
            has_courseuser=Exists(
                Courseuser.objects.filter(
                    user=user,
                    course=OuterRef('pk'),
                    status=self.PAYMENT_PASSED
                )
            ),
            is_bookmarked=Exists(
                Bookmark.objects.filter(
                    user=user,
                    content_type=course_content_type,
                    object_id=OuterRef('pk')
                )
            )
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user

        rewievs_list = Courserewievs.objects.filter(course=course).order_by('create')
        paginator = Paginator(rewievs_list, self.COMMENTS_PER_PAGE)

        page = self.request.GET.get('page')
        try:
            page_number = int(page)
        except (TypeError, ValueError):
            page_number = 1

        try:
            rewievs = paginator.page(page_number)
        except EmptyPage:
            # Если страница пуста, возвращаем последнюю страницу
            rewievs = paginator.page(paginator.num_pages)

        context['rewievs'] = rewievs

        context['user_courses'] = Courseuser.objects.filter(
            user=self.request.user,
            status=self.PAYMENT_PASSED
        ).values_list('course_id', flat=True)

        context['has_review'] = Courserewievs.objects.filter(course=course, user=user).exists()
        context['course_content_type_id'] = self.course_content_type.id

        return context


class MyCourseStudentView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'moderations/courses/mycourse_users.html'
    context_object_name = 'course'
    slug_field = "slug"

    PAYMENT_NOT_PASSED = 1
    PAYMENT_PASSED = 2

    COMMENTS_PER_PAGE = 4

    def get_queryset(self):
        user = self.request.user
        course_content_type = ContentType.objects.get_for_model(Course)
        self.course_content_type = course_content_type

        queryset = Course.objects.filter(draft=False).annotate(
            has_courseuser=Exists(
                Courseuser.objects.filter(
                    user=user,
                    course=OuterRef('pk'),
                    status=self.PAYMENT_PASSED
                )
            ),
            is_bookmarked=Exists(
                Bookmark.objects.filter(
                    user=user,
                    content_type=course_content_type,
                    object_id=OuterRef('pk')
                )
            )
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user

        rewievs_list = Courseuser.objects.filter(course=course, status=2).order_by('create')
        paginator = Paginator(rewievs_list, self.COMMENTS_PER_PAGE)

        page = self.request.GET.get('page')
        try:
            page_number = int(page)
        except (TypeError, ValueError):
            page_number = 1

        try:
            rewievs = paginator.page(page_number)
        except EmptyPage:
            # Если страница пуста, возвращаем последнюю страницу
            rewievs = paginator.page(paginator.num_pages)

        context['rewievs'] = rewievs

        context['user_courses'] = Courseuser.objects.filter(
            user=self.request.user,
            status=self.PAYMENT_PASSED
        ).values_list('course_id', flat=True)

        context['has_review'] = Courseuser.objects.filter(course=course, user=user).exists()
        context['course_content_type_id'] = self.course_content_type.id

        return context


class DeleteCourseReviewsView(LoginRequiredMixin, View):
    def post(self, request, rewievs_id):
        rewievs = get_object_or_404(Courserewievs, id=rewievs_id)

        if request.user.is_staff or request.user == rewievs.user:
            try:
                rewievs.delete()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Комментарий успешно удален.'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Ошибка при удалении комментария: {str(e)}'
                }, status=400)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'У вас нет прав для удаления этого комментария.'
            }, status=403)


class MyCourseSchedulesView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'moderations/courses/mycourse_schedules.html'
    context_object_name = 'course'
    slug_field = "slug"

    PAYMENT_NOT_PASSED = 1
    PAYMENT_PASSED = 2

    COMMENTS_PER_PAGE = 4

    def get_queryset(self):
        user = self.request.user
        course_content_type = ContentType.objects.get_for_model(Course)
        self.course_content_type = course_content_type

        queryset = Course.objects.filter(draft=False).annotate(
            has_courseuser=Exists(
                Courseuser.objects.filter(
                    user=user,
                    course=OuterRef('pk'),
                    status=self.PAYMENT_PASSED
                )
            ),
            is_bookmarked=Exists(
                Bookmark.objects.filter(
                    user=user,
                    content_type=course_content_type,
                    object_id=OuterRef('pk')
                )
            )
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user

        schedules_list = Schedulestream.objects.filter(themes__course=course).order_by('created_at')
        paginator = Paginator(schedules_list, self.COMMENTS_PER_PAGE)

        page = self.request.GET.get('page')
        try:
            page_number = int(page)
        except (TypeError, ValueError):
            page_number = 1

        try:
            schedules = paginator.page(page_number)
        except EmptyPage:
            # Если страница пуста, возвращаем последнюю страницу
            schedules = paginator.page(paginator.num_pages)

        context['schedules'] = schedules

        context['user_courses'] = Courseuser.objects.filter(
            user=self.request.user,
            status=self.PAYMENT_PASSED
        ).values_list('course_id', flat=True)

        context['has_schedules'] = Schedulestream.objects.filter(themes__course=course, users=user).exists()
        context['course_content_type_id'] = self.course_content_type.id

        return context


class GetUsersByScheduleView(LoginRequiredMixin, View):
    def get(self, request, schedule_id):
        schedule = Schedulestream.objects.get(id=schedule_id)
        users = schedule.users.all()

        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 20))

        # Получаем пользователей с учетом пагинации
        paginated_users = users[offset:offset + limit]

        user_list = [{'id': user.id, 'username': user.username, 'avatar': user.avatar.url} for user in paginated_users]
        return JsonResponse(user_list, safe=False)


class GetUsersByCourseView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = Course.objects.get(id=course_id)
        all_users = course.participants.all()

        # Получаем параметры offset, limit, query и selected_user_ids
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 20))
        query = request.GET.get('query', '')
        selected_user_ids = request.GET.getlist('selected_user_ids')

        # Разделяем пользователей на выбранных и невыбранных
        if selected_user_ids:
            selected_users = all_users.filter(id__in=selected_user_ids)
            non_selected_users = all_users.exclude(id__in=selected_user_ids)
        else:
            selected_users = all_users.none()
            non_selected_users = all_users

        # Фильтруем пользователей по запросу
        if query:
            selected_users = selected_users.filter(username__icontains=query)
            non_selected_users = non_selected_users.filter(username__icontains=query)

        # Объединяем выбранных и невыбранных пользователей
        sorted_users = list(selected_users) + list(non_selected_users)

        # Применяем пагинацию
        paginated_users = sorted_users[offset:offset + limit]

        # Формируем список для ответа
        user_list = [{'id': user.id, 'username': user.username, 'avatar': user.avatar.url, 'email': user.email} for user
                     in paginated_users]

        return JsonResponse(user_list, safe=False)


class RemoveUserFromScheduleView(LoginRequiredMixin, View):
    def delete(self, request, schedule_id, user_id):
        try:
            schedule = Schedulestream.objects.get(id=schedule_id)
            print(f"Расписание найдено: {schedule}")
            print(f"Пользователь для удаления: {user_id}")
            schedule.users.remove(user_id)
            print(f"Пользователь {user_id} удален из расписания {schedule_id}")
            return JsonResponse({'success': True}, status=204)
        except Schedulestream.DoesNotExist:
            print(f"Ошибка: расписание с ID {schedule_id} не найдено")
            return JsonResponse({'error': 'Schedule not found'}, status=404)
        except Exception as e:
            print(f"Ошибка при удалении пользователя: {e}")
            return JsonResponse({'error': str(e)}, status=400)


class DeleteCourseSchedulesView(LoginRequiredMixin, View):
    def post(self, request, schedules_id):
        schedules = get_object_or_404(Schedulestream, id=schedules_id)

        if request.user.is_staff:
            try:
                schedules.delete()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Расписание успешно удалено.'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Ошибка при удалении расписания: {str(e)}'
                }, status=400)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'У вас нет прав для удаления этого расписания.'
            }, status=403)


class MyCourseSchedulesCreateView(LoginRequiredMixin, View):
    def post(self, request, course_id):
        form = SchedulestreamForm(request.POST, request.FILES)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.link = str(uuid.uuid4())
            schedule.save()

            return HttpResponseRedirect(reverse('moderation:mycourse_schedules_update', args=[course_id, schedule.pk]))

        return HttpResponseRedirect(reverse('moderation:mycourse_schedules', args=[course_id]))


class MyCourseSchedulesUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'moderations/courses/edit_schedules.html'
    model = Schedulestream
    form_class = SchedulestreamForm
    context_object_name = 'schedules'

    def get_unique_username(self, base_username, email, User):
        username = base_username
        counter = 1

        while True:
            try:
                existing_user = User.objects.get(username=username)
                if existing_user.email == email:
                    return username, existing_user
                username = f"{base_username}{counter}"
                counter += 1
            except User.DoesNotExist:
                return username, None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs.get('course_id')
        context['course'] = Course.objects.get(id=course_id)
        context['excel_form'] = ExcelUploadForm()
        return context

    def post(self, request, *args, **kwargs):
        if 'excel_file' in request.FILES:
            excel_file = request.FILES['excel_file']

            # Проверка расширения файла
            file_ext = os.path.splitext(excel_file.name)[1]
            if file_ext.lower() not in ['.xlsx', '.xls']:
                messages.error(request, 'Пожалуйста, загрузите файл Excel (.xlsx или .xls)')
                return redirect(request.path)

            course_id = self.kwargs.get('course_id')
            course = Course.objects.get(id=course_id)
            schedule = self.get_object()

            try:
                # Чтение Excel файла
                df = pd.read_excel(excel_file)

                # Проверка наличия необходимых колонок
                required_columns = ['username', 'email']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    messages.error(request, f'В файле отсутствуют обязательные колонки: {", ".join(missing_columns)}')
                    return redirect(request.path)

                User = get_user_model()
                successful_imports = 0
                skipped_rows = 0

                for index, row in df.iterrows():
                    try:
                        # Получаем значения и удаляем пробелы
                        base_username = str(row['username']).strip() if pd.notna(row['username']) else ''
                        email = str(row['email']).strip() if pd.notna(row['email']) else ''

                        # Строгая проверка на пустые значения
                        if not base_username or not email:
                            messages.warning(
                                request,
                                f'Строка {index + 2} пропущена: Отсутствует {"username" if not base_username else "email"}'
                            )
                            skipped_rows += 1
                            continue

                        # Получаем уникальное имя пользователя
                        username, existing_user = self.get_unique_username(base_username, email, User)

                        if existing_user:
                            user = existing_user
                            if username != base_username:
                                messages.info(
                                    request,
                                    f'Строка {index + 2}: Пользователь с именем {base_username} и другим email уже существует. '
                                    f'Используется существующий пользователь с именем {username}'
                                )
                        else:
                            # Создаем нового пользователя
                            user = User(
                                username=username,
                                email=email,
                                gender=1,
                                type=1,
                                name=username,
                            )
                            user.set_password(username)
                            user.save()
                            messages.success(
                                request,
                                f'Строка {index + 2}: Создан новый пользователь {username}'
                                f'{" (изменено из-за конфликта)" if username != base_username else ""}'
                            )

                        # Добавление пользователя в курс и расписание
                        course.participants.add(user)
                        schedule.users.add(user)
                        successful_imports += 1

                    except Exception as row_error:
                        messages.error(request, f'Ошибка в строке {index + 2}: {str(row_error)}')
                        skipped_rows += 1
                        continue

                # Итоговое сообщение
                messages.success(
                    request,
                    f'Обработка файла завершена. Успешно импортировано: {successful_imports}, '
                    f'Пропущено строк: {skipped_rows}'
                )
                return redirect('moderation:mycourse_schedules', course_id=course_id)

            except Exception as e:
                messages.error(request, f'Ошибка при обработке файла: {str(e)}')

                import traceback
                print(traceback.format_exc())
                return redirect(request.path)

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        course_id = self.kwargs.get('course_id')
        self.success_url = reverse('moderation:mycourse_schedules', args=[course_id])
        return super().form_valid(form)


class SendUserPasswordView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        try:
            user = Profile.objects.get(id=user_id)
            send_mail(
                'Ваш пароль',
                f'Ваш пароль: {user.password}',
                'helpumother@helpumother.ru',
                [user.email],
                fail_silently=False,
            )
            return JsonResponse({'status': 'success'})
        except Profile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Пользователь не найден'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


class CourseDashboard(LoginRequiredMixin, TemplateView):
    model = Course
    template_name = 'moderations/courses/dashboard.html'
    context_object_name = 'course'
    slug_field = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = get_object_or_404(Course, pk=self.kwargs['pk'])
        context[self.context_object_name] = course

        context['reviews_count'] = Courserewievs.objects.filter(course=course).count()
        context['comments_count'] = Coursecomments.objects.filter(course=course).count()
        context['users_count'] = course.participants.count()
        context['assistents_count'] = CourseAssistents.objects.filter(course=course).count()
        context['finished_count'] = Courseuser.objects.filter(course=course, type=2).count()
        context['gained_count'] = Coursesertificateuser.objects.filter(course__course=course).count()
        context['modules_count'] = Modules.objects.filter(course=course).count()
        context['lecture_count'] = Themes.objects.filter(course=course).count()
        context['test_count'] = Qwiz.objects.filter(themes__course=course).exclude(type=1).count()
        context['seminar_count'] = Schedulestream.objects.filter(themes__course=course).count()
        context['reviews'] = Courserewievs.objects.filter(course=course).order_by('-create')
        context['comments'] = Coursecomments.objects.filter(course=course).order_by('-create')

        return context


class CourseCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Создаем новый курс
        course = Course.objects.create(
            author=request.user,
            price=0
        )

        # Создаем новый сертификат для курса
        Coursesertificate.objects.create(

            course=course,  # Связываем сертификат с этим курсом
            previev='default/certificate/defaultcert.png',  # Дефолтное изображение
            description='Описание сертификата'  # Описание, по желанию
        )

        # Перенаправляем на страницу редактирования курса
        return redirect(reverse('moderation:course_update', kwargs={'pk': course.id}))


# Список ассистентов


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class CourseAssistantsListView(ListView):
    model = CourseAssistents
    template_name = 'moderations/courses/course_assistants_list.html'
    context_object_name = 'assistants'
    paginate_by = 13

    def get_queryset(self):
        self.course = get_object_or_404(Course, id=self.kwargs['course_id'])
        return CourseAssistents.objects.filter(course=self.course)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course

        # Добавляем поиск преподавателей
        search_query = self.request.GET.get('q')
        if search_query:
            teachers = Profile.objects.filter(
                type=2
            ).filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(name__icontains=search_query)
            )[:10]  # Ограничиваем результаты поиска до 10
            context['search_results'] = teachers

        context['search_query'] = search_query or ''
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            search_results = context.get('search_results')
            if search_results:
                data = list(search_results.values('id', 'username', 'name', 'email'))
                return JsonResponse(data, safe=False)
        return super().render_to_response(context, **response_kwargs)


# Создание ассистента
class CourseAssistantCreateView(View):
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        author_id = request.POST.get('author_id')
        bookmark_as = request.POST.get('bookmark_as') == 'on'

        author = get_object_or_404(User, id=author_id)

        # Создаем ассистента в CourseAssistents, если он еще не существует
        course_assistant, created = CourseAssistents.objects.get_or_create(
            course=course,
            author=author,
            defaults={'bookmark_as': bookmark_as}
        )

        # Добавляем автора в Course.assistants, если его там еще нет
        if author not in course.assistants.all():
            course.assistants.add(author)

        # Возвращаем обновленный список
        assistants = CourseAssistents.objects.filter(course=course)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            assistant_data = [
                {
                    'id': assistant.author.id,
                    'name': assistant.author.get_full_name() or assistant.author.username,
                    'username': assistant.author.username,
                    'avatar_url': assistant.author.avatar.url if hasattr(assistant.author,
                                                                         'avatar') and assistant.author.avatar else None,
                    'bookmark_as': assistant.bookmark_as
                }
                for assistant in assistants
            ]
            return JsonResponse({'assistants': assistant_data})
        else:
            return render(request, 'moderations/courses/course_assistants_list.html', {
                'course': course,
                'assistants': assistants,
            })



# Редактирование ассистента
@method_decorator(csrf_exempt, name='dispatch')
class CourseAssistantUpdateView(View):
    def post(self, request, course_id, pk):
        try:
            # Проверка на наличие курса и ассистента
            course = get_object_or_404(Course, id=course_id)
            assistant = get_object_or_404(CourseAssistents, id=pk, course=course)

            # Обновление данных ассистента
            bookmark_as = request.POST.get('bookmark_as') == 'on'
            assistant.bookmark_as = bookmark_as
            assistant.save()

            # Возвращение успешного ответа
            return JsonResponse({'success': True})

        except Course.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Курс не найден'}, status=404)
        except CourseAssistents.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Ассистент не найден'}, status=404)


# Удаление ассистента
class CourseAssistantDeleteView(View):
    def post(self, request, course_id, pk):
        course = get_object_or_404(Course, id=course_id)
        assistant = get_object_or_404(CourseAssistents, id=pk, course=course)

        # Удаляем ассистента из CourseAssistents
        assistant.delete()

        # Удаляем ассистента из Course.assistants
        course.assistants.remove(assistant.author)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        else:
            # Возвращаем обновленный список
            assistants = CourseAssistents.objects.filter(course=course)
            return render(request, 'moderations/courses/course_assistants_list.html', {
                'course': course,
                'assistants': assistants,
            })


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class CourseUpdateView(View):
    template_name = 'moderations/courses/course_create_iframe.html'

    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk)

        if not self.has_permission(request.user, course):
            return HttpResponseForbidden("У вас нет прав для редактирования этого курса.")

        modules = course.modules_set.all().order_by('position')

        # Предзагружаем темы для каждого модуля
        modules_with_themes = modules.prefetch_related(
            Prefetch('modulescourse',
                     queryset=Themes.objects.order_by('position'),
                     to_attr='themes_list')
        )

        # Получаем темы, не привязанные к модулям
        themes_without_module = course.themescourse.filter(modules__isnull=True).order_by('position')

        context = {
            'course': course,
            'modules_with_themes': modules_with_themes,
            'themes_without_module': themes_without_module,
            'all_categories': CategorysCourse.objects.all(),
        }

        return render(request, self.template_name, context)

    def has_permission(self, user, course):
        return user == course.author or user in course.assistants.all()


# Get Курсов

User = get_user_model()

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class CourseDataView(View):
    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        return JsonResponse(self.course_to_dict(course))

    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk)

        # Обновление простых полей
        course.name = request.POST.get('name', course.name)
        course.slug = request.POST.get('slug', course.slug)
        course.description = request.POST.get('description', course.description)
        course.title = request.POST.get('title', course.title)
        course.content = request.POST.get('content', course.content)
        course.propertytitle = request.POST.get('propertytitle', course.propertytitle)
        course.propertydescription = request.POST.get('propertydescription', course.propertydescription)
        if request.POST.get('action') == 'publish':
            course.draft = not course.draft  # Инвертируем значение

        # Обработка цены
        try:
            course.price = int(request.POST.get('price', 0))
        except ValueError:
            course.price = 0

        # Обработка категорий
        category_ids = request.POST.getlist('category')
        valid_category_ids = [int(cat_id) for cat_id in category_ids if cat_id.isdigit()]
        course.category.set(CategorysCourse.objects.filter(id__in=valid_category_ids))

        # Обработка ассистентов
        assistant_ids = request.POST.getlist('assistants')
        valid_assistant_ids = [int(asst_id) for asst_id in assistant_ids if asst_id.isdigit()]
        course.assistants.set(User.objects.filter(id__in=valid_assistant_ids))

        # Обработка файлов
        if 'cover' in request.FILES:
            course.cover = request.FILES['cover']
        if 'image' in request.FILES:
            course.image = request.FILES['image']
        if 'previev' in request.FILES:
            course.previev = request.FILES['previev']

        try:
            course.save()
            # Рендерим обновленную форму
            context = {
                'course': course,
                'all_categories': CategorysCourse.objects.all(),
                'all_assistants': User.objects.filter(is_staff=True),
            }
            return render(request, 'moderations/courses/add_course_form.html', context)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    def course_to_dict(self, course):
        return {
            'id': str(course.pk),
            'name': course.name,
            'slug': course.slug,
            'description': course.description,
            'cover': course.cover.url if course.cover else None,
            'image': course.image.url if course.image else None,
            'previev': course.previev.url if course.previev else None,
            'category': list(course.category.values('id', 'name')),
            'title': course.title,
            'content': course.content,
            'propertytitle': course.propertytitle,
            'propertydescription': course.propertydescription,
            'price': course.price,
            'assistants': list(course.assistants.values('id', 'email')),
            'all_categories': list(CategorysCourse.objects.values('id', 'name')),
            'all_assistants': list(User.objects.filter(is_staff=True).values('id', 'email'))
        }

@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user == course.author:
        try:
            # Удаление курса
            course.delete()

            # Проверка на AJAX-запрос по заголовку
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Использование reverse для получения URL по имени маршрута
                redirect_url = reverse('moderation:mycourses')
                return JsonResponse({'status': 'success', 'redirect_url': redirect_url})

            # Стандартный редирект для обычного запроса
            return redirect('moderation:mycourses')

        except Exception as e:
            # Обработка ошибки при удалении
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': f'Ошибка при удалении курса: {str(e)}'}, status=400)

            # При ошибке при обычном запросе можно добавить обработку или оставить стандартный редирект
            return redirect('moderation:mycourses')

    # Если пользователь не автор курса
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'error', 'message': 'У вас нет прав для удаления этого курса.'}, status=403)

    return redirect('moderation:mycourses')

class ThemesCreateView(View):
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        name = request.POST.get('name')
        description = request.POST.get('description')
        module_id = request.POST.get('module')
        point = request.POST.get('point')
        point_status = request.POST.get('point_status') == 'on'
        access_type = request.POST.get('access_type') == 'on'
        attempts_status = request.POST.get('attempts_status') == 'on'
        attempts = request.POST.get('attempts')
        test_duration = request.POST.get('test_duration')
        show_answer = request.POST.get('show_answer') == 'on'
        home_work = request.POST.get('home_work_add_themes')
        home_work_status = request.POST.get('home_work_status') == 'on'

        errors = {}
        if not name:
            errors['name'] = 'Это поле обязательно.'
        if not description:
            errors['description'] = 'Это поле обязательно.'

        if not errors:
            module = Modules.objects.filter(id=module_id, course=course).first() if module_id else None
            last_position = Themes.objects.filter(modules=module or None, course=course).order_by('-position').first()
            new_position = (last_position.position + 1) if last_position else 1

            theme = Themes.objects.create(
                course=course,
                modules=module,
                name=name,
                description=description,
                position=new_position,
                point=int(point) if point else None,
                point_status=point_status,
                access_type=access_type,
                attempts_status=attempts_status,
                attempts=int(attempts) if attempts else None,
                test_duration=test_duration,
                show_answer=show_answer,
                home_work=home_work,
                home_work_status=home_work_status
            )

            logger.debug(f"Создана новая тема: {theme.id} - {theme.name}")

            response_data = {
                'success': True,
                'success_message': 'Тема успешно создана!',
                'theme': {
                    'id': theme.id,
                    'name': theme.name,
                    'description': theme.description,
                    'position': theme.position,
                    'module_id': module.id if module else None,
                }
            }
        else:
            logger.debug(f"Ошибки при создании темы: {errors}")
            response_data = {
                'success': False,
                'errors': errors,
            }

        return JsonResponse(response_data)

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        modules = Modules.objects.filter(course=course).order_by('position')

        context = {
            'modules': list(modules.values('id', 'name')),
        }
        return JsonResponse(context)


class ThemesDeleteView(View):
    def post(self, request, theme_id):
        theme = get_object_or_404(Themes, id=theme_id)
        course = theme.course
        position = theme.position

        # Удаляем тему
        theme.delete()

        # Если у темы была позиция, сдвигаем позиции остальных
        if position is not None:
            Themes.objects.filter(
                course=course,
                position__gt=position
            ).update(position=F('position') - 1)

        # Возвращаем успешный ответ с сообщением
        return JsonResponse({
            'success': True,
            'message': 'Тема успешно удалена',
        })


class QwizDeleteView(View):
    def post(self, request, quiz_id):
        # Получаем квиз по ID или 404 ошибку
        qwiz = get_object_or_404(Qwiz, id=quiz_id)

        # Сохраняем тему и позицию удаляемого квиза
        theme = qwiz.themes
        position = qwiz.position

        # Удаляем квиз
        qwiz.delete()

        # Если у квиза была позиция, сдвигаем позиции остальных
        if position is not None:
            Qwiz.objects.filter(
                themes=theme,
                position__gt=position
            ).update(position=F('position') - 1)

        # Возвращаем успешный ответ с сообщением
        return JsonResponse({
            'success': True,
            'message': 'Квиз успешно удален',
        })


class QuestionDeleteView(View):
    def post(self, request, quiz_id, question_id):
        # Получаем квиз и вопрос по их ID
        qwiz = get_object_or_404(Qwiz, id=quiz_id)
        question = get_object_or_404(Question, id=question_id, qwiz=qwiz)

        # Удаляем вопрос
        question.delete()

        # Возвращаем успешный ответ
        return JsonResponse({
            'success': True,
            'message': 'Вопрос успешно удален',
        })


class ThemesEditView(View):
    def post(self, request, theme_id):
        theme = get_object_or_404(Themes, id=theme_id)
        name = request.POST.get('name')
        description = request.POST.get('description_edit_themes')
        module_id = request.POST.get('module')
        point = request.POST.get('point')
        point_status = request.POST.get('point_status') == 'on'
        access_type = request.POST.get('access_type') == 'on'
        attempts_status = request.POST.get('attempts_status') == 'on'
        attempts = request.POST.get('attempts')
        test_duration = request.POST.get('test_duration')
        show_answer = request.POST.get('show_answer') == 'on'
        home_work = request.POST.get('home_work_edit_themes')
        home_work_status = request.POST.get('home_work_status') == 'on'

        errors = {}
        if not name:
            errors['name'] = 'Это поле обязательно.'
        if not description:
            errors['description'] = 'Это поле обязательно.'

        if not module_id:
            errors['module'] = 'Выберите модуль.'

        if not errors:
            module = get_object_or_404(Modules, id=module_id, course=theme.course)

            theme.name = name
            theme.description = description
            theme.modules = module
            theme.point = int(point) if point else None
            theme.point_status = point_status
            theme.access_type = access_type
            theme.attempts_status = attempts_status
            theme.attempts = int(attempts) if attempts else None
            theme.test_duration = test_duration
            theme.show_answer = show_answer
            theme.home_work = home_work
            theme.home_work_status = home_work_status
            theme.save()

            return JsonResponse({
                'success': True,
                'theme_id': theme.id,  # Добавляем ID темы
                'new_title': theme.name  # Добавляем новое название темы
            })

        else:
            return JsonResponse({'errors': errors}, status=400)

class ThemesEditGetView(View):
    def get(self, request, theme_id):
        theme = get_object_or_404(Themes, id=theme_id)
        files = Files.objects.filter(theme=theme)
        context = {
            'theme_id': theme_id,
            'theme': theme,
            'files': files,
            'modules': Modules.objects.filter(course=theme.course).order_by('position'),
            'errors': {}
        }

        # Рендерим шаблон для формы, но не с использованием render_to_string в ответе
        form_html = render_to_string('moderations/courses/edit_theme_form.html', context, request=request)

        return JsonResponse({
            'form_html': form_html
        })


class FileUploadView(View):
    def post(self, request, theme_id):
        theme = get_object_or_404(Themes, id=theme_id)
        file = request.FILES.get('file')
        file_name = request.POST.get('file_name')

        if file and file_name:
            # Определяем тип файла на основе расширения
            _, extension = os.path.splitext(file_name.lower())

            if extension in ['.mp4', '.avi', '.mov', '.wmv']:
                file_type = 1  # Видео
            elif extension in ['.mp3', '.wav', '.ogg', '.flac']:
                file_type = 2  # Аудио
            else:
                file_type = 3  # Документ

            new_file = Files.objects.create(
                theme=theme,
                files=file,
                name=file_name,
                type=file_type
            )

            return JsonResponse({
                'status': 'success',
                'file_id': new_file.id,
                'file_name': new_file.name,
                'file_type': new_file.get_type_display()
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'No file or file name provided'
            }, status=400)


class UpdateFileLinkView(View):
    def post(self, request, file_id):
        file = get_object_or_404(Files, id=file_id)
        file.link = True
        file.save()

        # Возвращаем JSON-ответ с данными для обновления
        return JsonResponse({'link': file.link, 'file_id': file.id, 'video_url': file.files.url})


class FileDeleteView(View):
    def post(self, request, file_id):
        file = get_object_or_404(Files, id=file_id)
        file.delete()
        return JsonResponse({'status': 'success'})


@csrf_exempt
def file_upload(request):
    if request.method == 'POST' and request.FILES.get('files'):
        uploaded_file = request.FILES['files']
        file_name = default_storage.save(uploaded_file.name, uploaded_file)
        file_url = default_storage.url(file_name)
        return JsonResponse({'file_path': file_url})
    return JsonResponse({'error': 'No file uploaded'}, status=400)


@require_POST
@transaction.atomic
def move_theme(request, theme_id, direction, position):
    try:
        with transaction.atomic():
            theme = Themes.objects.select_for_update().get(id=theme_id)
            course = theme.course

            # Проверка на соответствие позиции
            if theme.position != position:
                return JsonResponse({'error': 'Несоответствие позиции'}, status=400)

            if direction == 'up' and theme.position > 1:
                # Находим предыдущую тему и меняем позиции
                previous_theme = Themes.objects.select_for_update().filter(
                    course=course,
                    position=theme.position - 1
                ).first()

                if previous_theme:
                    previous_theme.position = theme.position
                    theme.position -= 1
                    previous_theme.save()
                    theme.save()

            elif direction == 'down':
                # Находим следующую тему и меняем позиции
                next_theme = Themes.objects.select_for_update().filter(
                    course=course,
                    position=theme.position + 1
                ).first()

                if next_theme:
                    next_theme.position = theme.position
                    theme.position += 1
                    next_theme.save()
                    theme.save()

        modules_with_themes = Modules.objects.filter(
            course=course
        ).prefetch_related('modulescourse').order_by('position')

        themes_without_module = Themes.objects.filter(
            course=course,
            modules__isnull=True
        ).order_by('position')

        context = {
            'course': course,
            'modules_with_themes': modules_with_themes,
            'themes_without_module': themes_without_module,
        }

        html = render_to_string('moderations/courses/themes_list.html', context, request=request)
        return HttpResponse(html)

    except Themes.DoesNotExist:
        return JsonResponse({'error': 'Тема не найдена'}, status=404)
    except Exception as e:
        print(f"Ошибка при перемещении темы: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@transaction.atomic
def move_quiz(request, quiz_id, direction, position):
    print(f"Received request: quiz_id={quiz_id}, direction={direction}, position={position}")
    if request.method == 'POST':
        try:
            with transaction.atomic():
                quiz = Qwiz.objects.select_for_update().get(id=quiz_id)
                themes_id = quiz.themes_id

                # Проверка на соответствие позиции
                if quiz.position != position:
                    return JsonResponse({'error': 'Несоответствие позиции'}, status=400)

                if direction == 'up' and quiz.position > 1:
                    # Находим предыдущий квиз и меняем позиции
                    previous_quiz = Qwiz.objects.select_for_update().filter(
                        themes_id=themes_id,
                        position=quiz.position - 1
                    ).first()

                    if previous_quiz:
                        previous_quiz.position = quiz.position
                        quiz.position -= 1
                        previous_quiz.save()
                        quiz.save()

                elif direction == 'down':
                    # Находим следующий квиз и меняем позиции
                    next_quiz = Qwiz.objects.select_for_update().filter(
                        themes_id=themes_id,
                        position=quiz.position + 1
                    ).first()

                    if next_quiz:
                        next_quiz.position = quiz.position
                        quiz.position += 1
                        next_quiz.save()
                        quiz.save()

                # Получаем все квизы в теме с обновленными позициями
                quizzes = Qwiz.objects.filter(themes_id=themes_id).order_by('position')
                quiz_positions = [{'id': q.id, 'position': q.position} for q in quizzes]

                return JsonResponse({
                    'success': True,
                    'newPosition': quiz.position,
                    'quizzes': quiz_positions  # Возвращаем новые позиции всех квизов
                })

        except Qwiz.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Квиз не найден'}, status=404)
        except Exception as e:
            print(f"Ошибка при перемещении квиза: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'}, status=400)



class ThemeDetailView(View):
    def get(self, request, *args, **kwargs):
        theme_id = request.GET.get('theme_id')
        logger.debug(f"Received request for theme_id: {theme_id}")

        try:
            theme = get_object_or_404(Themes, id=theme_id)
            logger.debug(f"Found theme: {theme}")
            files = Files.objects.filter(theme=theme)
            logger.debug(f"Found {files.count()} files for theme")

            context = {
                'themes': theme,
                'files': files,
            }

            html = render_to_string('moderations/courses/views-themes.html', context)
            logger.debug("Rendered HTML template")

            data = {
                'html': html,
            }

            return JsonResponse(data)
        except Exception as e:
            logger.error(f"Error in ThemeDetailView: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)


class QwizDetailView(View):
    def get(self, request, *args, **kwargs):
        qwiz_id = request.GET.get('qwiz_id')
        logger.debug(f"Received request for qwiz_id: {qwiz_id}")

        try:
            qwiz = get_object_or_404(Qwiz, id=qwiz_id)
            questions = Question.objects.filter(qwiz=qwiz)
            logger.debug(f"Found qwiz: {qwiz}")

            context = {
                'qwiz': qwiz,
                'questions': questions,
            }

            html = render_to_string('moderations/courses/views-qwiz.html', context)
            logger.debug("Rendered HTML template")

            data = {
                'html': html,
            }

            return JsonResponse(data)
        except Exception as e:
            logger.error(f"Error in QwizDetailView: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class ModuleCreateView(View):
    def post(self, request, course_id, *args, **kwargs):
        name = request.POST.get('name')

        if course_id and name:
            try:
                course = Course.objects.get(id=course_id)

                # Получаем последнюю позицию
                last_module = Modules.objects.filter(course=course).order_by('-position').first()
                new_position = (last_module.position or 0) + 1 if last_module else 1

                # Создаем новый модуль с вычисленной позицией
                module = Modules.objects.create(
                    course=course,
                    name=name,
                    position=new_position
                )

                return JsonResponse({'success': True, 'module': model_to_dict(module)})
            except Course.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Курс не найден.'})

        return JsonResponse({'success': False, 'error': 'Неверные данные.'})

    def get(self, request, *args, **kwargs):
        return JsonResponse({'success': False, 'error': 'Только метод POST поддерживается.'})

class UpdateCourseSettingsView(View):
    template_name = 'moderations/courses/settings.html'

    def post(self, request, course_id, *args, **kwargs):
        course_type = request.POST.get('access')
        start_dates = request.POST.getlist('public_start_date[]')
        end_dates = request.POST.getlist('public_end_date[]')
        setting_ids = request.POST.getlist('setting_id[]')
        action = request.POST.get('action')
        setting_id_to_delete = request.POST.get('setting_id_to_delete')

        course = get_object_or_404(Course, id=course_id)

        # Если это запрос на удаление
        if action == 'delete' and setting_id_to_delete:
            try:
                setting = CourseSettings.objects.get(id=setting_id_to_delete, course=course)
                setting.delete()
                return JsonResponse({'success': True})
            except CourseSettings.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Setting not found'}, status=404)

        if course_type is not None:
            access_mapping = {
                'public': 1,
                'selected': 2,
                'private': 3,
            }
            course.type = access_mapping.get(course_type, course.type)
            course.save()

        existing_settings = {}
        for setting_id, start_date, end_date in zip(setting_ids, start_dates, end_dates):
            start_date_parsed = parse_date(start_date)
            end_date_parsed = parse_date(end_date)

            if not (start_date_parsed and end_date_parsed):
                continue

            date_key = (start_date_parsed, end_date_parsed)
            if date_key in existing_settings:
                continue

            existing_settings[date_key] = True

            if setting_id:
                try:
                    setting = CourseSettings.objects.get(id=setting_id, course=course)
                    setting.data_start = start_date_parsed
                    setting.data_end = end_date_parsed
                    setting.save()
                except CourseSettings.DoesNotExist:
                    CourseSettings.objects.create(
                        course=course,
                        data_start=start_date_parsed,
                        data_end=end_date_parsed
                    )
            else:
                if not CourseSettings.objects.filter(
                    course=course,
                    data_start=start_date_parsed,
                    data_end=end_date_parsed
                ).exists():
                    CourseSettings.objects.create(
                        course=course,
                        data_start=start_date_parsed,
                        data_end=end_date_parsed
                    )

        return JsonResponse({'success': True})

    def get(self, request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, id=course_id)
        course_settings = CourseSettings.objects.filter(course=course).order_by('data_start')

        return render(request, self.template_name, {
            'course': course,
            'course_settings': course_settings
        })



class UpdateCourseCertificateView(View):
    template_name = 'moderations/courses/certificate-create.html'

    def get(self, request, course_id):
        # Получение объекта сертификата по ID курса
        certificate = get_object_or_404(Coursesertificate, course_id=course_id)
        print(f"GET request received for course_id: {course_id}")
        print(f"Certificate details: {certificate}")

        context = {
            'course': Course.objects.get(id=course_id),
            'certificate': certificate,  # Передача самого объекта сертификата в шаблон
        }
        print(f"Context for template: {context}")

        # Рендеринг шаблона
        return render(request, self.template_name, context)

    def post(self, request, course_id):
        print(f"POST request received for course_id: {course_id}")

        # Получение объекта сертификата
        certificate = get_object_or_404(Coursesertificate, course_id=course_id)
        print(f"Certificate before update: {certificate}")

        # Получение данных из запроса
        description = request.POST.get('description')
        previev = request.FILES.get('previev')
        height = request.POST.get('height')  # Получение высоты
        width = request.POST.get('width')  # Получение ширины

        print(f"Description from form: {description}")
        print(f"Preview file: {previev}")
        print(f"Height from form: {height}")
        print(f"Width from form: {width}")

        # Обновление данных
        if description:
            certificate.description = description
        if previev:
            certificate.previev = previev

        # Приведение высоты и ширины к int
        if height:
            try:
                certificate.height = int(float(height))  # Приведение к float, затем к int
            except ValueError:
                print(f"Invalid height value: {height}")

        if width:
            try:
                certificate.width = int(float(width))  # Приведение к float, затем к int
            except ValueError:
                print(f"Invalid width value: {width}")

        # Переключение значения published при каждом POST-запросе
        if request.POST.get('action') == 'publish':
            certificate.published = not certificate.published  # Инвертируем значение
            print(f"Certificate will be {'published' if certificate.published else 'unpublished'}.")

        # Сохранение изменений в базе данных
        certificate.save()
        print(f"Certificate after update: {certificate}")

        # Возврат ответа
        return JsonResponse({'status': 'success', 'message': 'Certificate updated successfully'})


class VideoChatRoomListView(ListView):
    model = VideoChatRoom
    template_name = 'moderations/courses/conference_list.html'
    paginate_by = 20

    def get(self, request, course_id):
        context = {
            'course': Course.objects.get(id=course_id),
        }
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



        # Рендеринг шаблона
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class ConferenceEventsView(View):
    def get(self, request, course_id, *args, **kwargs):
        # Получаем курс или возвращаем 404
        course = get_object_or_404(Course, id=course_id)

        # Фильтруем события, относящиеся к этому курсу
        schedules = VideoChatRoom.objects.filter(course=course)
        events = []

        # Формируем данные событий
        for schedule in schedules:
            try:
                event = {
                    'title': schedule.name,
                    'time_start': schedule.start_time.isoformat(),
                    'time_end': schedule.end_time.isoformat(),
                    'date': schedule.start_data.isoformat(),
                    'description': schedule.descriptions,
                    'room_slug': schedule.slug,  # Используем slug вместо id
                }
                events.append(event)
            except AttributeError as e:
                print(f"Error processing schedule {schedule.id}: {str(e)}")
                events.append({
                    'title': 'Error: Event data not available',
                    'time_start': None,
                    'time_end': None,
                    'date': None,
                    'description': 'Error: Description not available',
                    'room_slug': None,
                })

        # Возвращаем JSON-ответ
        return JsonResponse(events, safe=False)

class EditModuleView(LoginRequiredMixin, View):
    def post(self, request, module_id):
        print(f"EditModuleView called with module_id: {module_id}")

        module = get_object_or_404(Modules, id=module_id)
        print(f"Module found: {module.name}")

        if not self.has_permission(request.user, module.course):
            return JsonResponse({'success': False, 'error': 'У вас нет прав для редактирования этого модуля.'})

        name = request.POST.get('name')
        if name:
            module.name = name
            module.save()
            print(f"Module name updated to: {name}")
        else:
            return JsonResponse({'success': False, 'error': 'Имя модуля не может быть пустым.'})

        # Возвращаем только обновленное имя
        return JsonResponse({'success': True, 'updated_name': module.name})

    def has_permission(self, user, course):
        return user == course.author or user in course.assistants.all()


class DeleteModuleView(LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request, module_id):
        module = get_object_or_404(Modules, id=module_id)

        # Проверка прав доступа
        if not self.has_permission(request.user, module.course):
            return JsonResponse({'success': False, 'message': 'У вас нет прав для удаления этого модуля.'}, status=403)

        # Получаем курс, к которому принадлежит модуль
        course = module.course

        # Получаем все темы модуля перед его удалением
        themes = list(module.modulescourse.all())

        # Сохраняем позицию модуля для сдвига других модулей
        position = module.position

        # Удаляем модуль
        module.delete()

        # Если у модуля была позиция, сдвигаем позиции остальных модулей в курсе
        if position is not None:
            Modules.objects.filter(
                course=course,
                position__gt=position
            ).update(position=F('position') - 1)

        # Возвращаем успешный ответ
        return JsonResponse({
            'success': True,
            'message': 'Модуль успешно удален',
        })

    def has_permission(self, user, course):
        return user == course.author or user in course.assistants.all()

@csrf_exempt
@transaction.atomic
def move_module(request, module_id, direction):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                module = Modules.objects.select_for_update().get(id=module_id)
                current_position = module.position
                course_id = module.course_id

                # Проверка прав доступа

                if direction == 'up' and current_position > 1:
                    previous_module = Modules.objects.select_for_update().filter(
                        course_id=course_id,
                        position=current_position - 1
                    ).first()

                    if previous_module:
                        previous_module.position = current_position
                        module.position = current_position - 1
                        previous_module.save()
                        module.save()

                elif direction == 'down':
                    next_module = Modules.objects.select_for_update().filter(
                        course_id=course_id,
                        position=current_position + 1
                    ).first()

                    if next_module:
                        next_module.position = current_position
                        module.position = current_position + 1
                        next_module.save()
                        module.save()

                return JsonResponse({
                    'success': True,
                    'newPosition': module.position  # Возвращаем новую позицию
                })

        except Modules.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Модуль не найден'}, status=404)
        except Exception as e:
            print(f"Ошибка при перемещении модуля: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'}, status=400)


class QwizCreateView(View):
    """Создание теста"""

    def post(self, request, *args, **kwargs):

        theme_id = request.POST.get('theme_id')
        name = request.POST.get('name')
        if request.POST.get('type'):
            qwiz_type = int(request.POST.get('type'))
        else:
            qwiz_type = 6
            print('-------------------',request.POST.get('type'))
        description = request.POST.get('description')
        point = request.POST.get('point')
        hints = {key: value for key, value in request.POST.items() if key.startswith('hint_')}

        if not name:
            return JsonResponse({"message": "Поле 'Название теста' обязательно для заполнения!"}, status=400)

        theme = get_object_or_404(Themes, id=theme_id)

        # Получаем последнюю позицию для тем в текущем модуле или курсе
        if theme:
            last_position = Qwiz.objects.filter(themes=theme).order_by('-position').first()
        else:
            last_position = Qwiz.objects.filter(themes=theme, themes__isnull=True).order_by('-position').first()
        new_position = (last_position.position or 0) + 1 if last_position else 1


        qwiz = Qwiz.objects.create(
            themes=theme,
            name=name,
            type=qwiz_type,
            position=new_position,
            description=description or "",
            point=point,
        )

        def get_right_answer(value):
            return 2 if value == 'on' else 1

        if qwiz_type == 2:  # Тесты
            questions_data = request.POST.getlist('qwiz_title_type_2[]')
            right_answers = request.POST.getlist('qwiz_right_answer_type_2[]')

            print(f"Questions: {questions_data}")
            print(f"Right Answers: {right_answers}")

            for question_title, right_answer in zip(questions_data, right_answers):
                answer_value = get_right_answer(right_answer)
                print(f"Creating question: {question_title}, right answer: {answer_value}")
                Question.objects.create(
                    qwiz=qwiz,
                    title=question_title,
                    right_answer=answer_value,
                    description=""  # Добавляем пустое описание, так как оно обязательно
                )

        elif qwiz_type == 3:  # Тесты с картинками
            right_answers = request.POST.getlist('qwiz_right_answer_type_3[]')
            images = request.FILES.getlist('image-qwiz-type-3[]')
            questions_data = request.POST.getlist('qwiz_title_type_3[]')

            print(f"Right Answers: {right_answers}")
            print(f"Images: {images}")

            for right_answer, image,questiondata in zip(right_answers, images, questions_data):
                answer_value = get_right_answer(right_answer)
                print(f"Creating question with image: right answer: {answer_value}")
                Question.objects.create(
                    qwiz=qwiz,
                    title=questiondata,
                    right_answer=answer_value,
                    image=image,
                    description=""  # Пустое описание, если оно обязательно
                )
        elif qwiz_type == 4:  # Выборка
            questions_data_4_1 = request.POST.getlist('qwiz_title_type_4_1[]')
            questions_data_4_2 = request.POST.getlist('qwiz_title_type_4_2[]')
            right_answers = request.POST.getlist('qwiz_right_answer_type_4_1[]')

            print(f"Questions 4_1: {questions_data_4_1}")
            print(f"Questions 4_2: {questions_data_4_2}")
            print(f"Right Answers 4_1: {right_answers}")

            for question_title_1, question_title_2, right_answer in zip(questions_data_4_1, questions_data_4_2, right_answers):
                answer_value = get_right_answer(right_answer)
                print(f"Question 1: {question_title_1}, question 2: {question_title_2}, right answer: {answer_value}")
                Question.objects.create(
                    qwiz=qwiz,
                    title=question_title_1,
                    second_title=question_title_2,
                    right_answer=answer_value,
                    description=""  # Добавляем пустое описание, так как оно обязательно
                )

        elif qwiz_type == 5:  # Заполните пропуск
            # Получаем данные для вопросов
            descriptions_data = request.POST.getlist('qwiz_description_type_5[]')
            print(f"Descriptions: {descriptions_data}")

            # Перебор всех подсказок и их статусов
            hints_data = {}
            statuses_data = {}

            for key in request.POST:
                if key.startswith('hint_'):  # Ищем подсказки по префиксу
                    parts = key.split('_')
                    print(f"hint_ parts: {parts}")
                    # Проверка: ключ должен содержать хотя бы 3 части
                    if len(parts) >= 2 and parts[1].isdigit():
                        question_id = int(parts[1])
                        print(f"hint_ question_id : {question_id}")
                        if question_id not in hints_data:
                            hints_data[question_id] = []
                        hints_data[question_id].extend(request.POST.getlist(key))  # Используем getlist, если это массив
                    else:
                        print(f"Неверный формат ключа: {key}")

                # Обработка статусов правильных ответов для подсказок
                if key.startswith('qwiz_right_answer_type_5_'):  # Ищем статусы правильных ответов
                    parts = key.split('_')
                    print(f" qwiz_right_answer_type_5 parts: {parts}")
                    # Проверка: ключ должен содержать хотя бы 3 части
                    if len(parts) >= 3 and parts[5].isdigit():
                        question_id = int(parts[5])  # Извлекаем ID вопроса
                        print(f"qwiz_right_answer_type_5 question_id : {question_id}")
                        if question_id not in statuses_data:
                            statuses_data[question_id] = []
                        statuses_data[question_id].extend(request.POST.getlist(key))  # Используем getlist для массивов
                    else:
                        print(f"Неверный формат ключа: {key}")

            print(f"Hints: {hints_data}")
            print(f"Statuses: {statuses_data}")

            # Проверяем, что количество подсказок и статусов совпадает
            for question_id in hints_data:
                if len(hints_data[question_id]) != len(statuses_data[question_id]):
                    print(f"Несоответствие количества подсказок и статусов для вопроса {question_id}")

            # Создание вопросов и привязка подсказок
            for idx, description_value in enumerate(descriptions_data):
                if description_value.strip():  # Пропускаем пустые описания
                    question = Question.objects.create(
                        qwiz=qwiz,
                        title="",
                        description=description_value,
                        right_answer=1  # Устанавливаем по умолчанию значение для правильного ответа
                    )
                    print(f"Создан вопрос с описанием: {description_value}")

                    # Создаем и привязываем подсказки к вопросу
                    for hint_idx, hint_name in enumerate(hints_data.get(idx, [])):
                        if hint_name:
                            status = 2 if statuses_data.get(idx, [])[hint_idx] == 'on' else 1
                            hint = HintsToQuestion.objects.create(
                                name=hint_name,
                                right_answer=status
                            )
                            question.hints.add(hint)

                    question.save()
        elif qwiz_type == 6:
            request.POST
            indices_left = {
                key.split("_")[-1]
                for key in request.POST.keys()
                if key.startswith("qwiz_title_type_6_")
            }
            indices_right = {
                key.split("_")[-1]
                for key in request.POST.keys()
                if key.startswith("qwiz_title_type_second_6_")
            }
            # Объединяем множества индексов
            indices = indices_left.union(indices_right)
            # Сортируем по числовому значению
            indices = sorted(indices, key=lambda x: int(x))
            print("indices---------------", indices_left)
            print("indices---------------", indices_right)
            print("indices sort---------------", indices)

            blocks = []
            for idx in indices:
                left_text = request.POST.get("qwiz_title_type_6_" + idx, "")
                right_text = request.POST.get("qwiz_title_type_second_6_" + idx, "")
                left_file = request.FILES.get("image-qwiz-type-6_" + idx)
                right_file = request.FILES.get("image-qwiz-type-second-6_" + idx)

                Question.objects.create(
                    qwiz=qwiz,
                    right_answer = 2,
                    title = name,
                    left_text = left_text,
                    left_file = left_file,
                    right_text=right_text,
                    right_file=right_file,
                )

        return JsonResponse({"message": "Тест успешно сохранен!"}, status=200)


class QwizUpdateView(View):
    """Получение и обновление теста"""

    def get(self, request, quiz_id):
        qwiz = get_object_or_404(Qwiz, id=quiz_id)
        questions = Question.objects.filter(qwiz=qwiz)
        context = {
            'quiz': qwiz,
            'questions': questions,
            'errors': {}
        }
        form_html = render_to_string('moderations/courses/edit_qwiz.html', context, request=request)
        return HttpResponse(form_html)



    def post(self, request, quiz_id, *args, **kwargs):
        """
        Обновить тест и вопросы по ID.
        """
        # Получаем тест по ID
        qwiz = get_object_or_404(Qwiz, id=quiz_id)

        # Получаем данные из запроса
        name = request.POST.get('name')
        description = request.POST.get('description')
        qwiz_type = int(request.POST.get('type'))
        qwiz_point = int(request.POST.get('point'))

        # Проверка на обязательность названия теста
        if not name:
            return JsonResponse({"message": "Поле 'Название теста' обязательно для заполнения!"}, status=400)

        # Обновляем тест
        qwiz.name = name
        qwiz.description = description or ""
        qwiz.type = qwiz_type
        qwiz.point = qwiz_point
        qwiz.save()

        def get_right_answer(value):
            return 2 if value == 'on' else 1

        # Обрабатываем вопросы в зависимости от типа теста
        if qwiz_type == 2:  # Тесты (без картинок)
            questions_data = request.POST.getlist('editqwiz_title_type_2[]')
            right_answers = request.POST.getlist('editqwiz_right_answer_type_2[]')
            print(f"Questions: {questions_data}")
            print(f"Right Answers (before filtering): {right_answers}")

            # Удаляем лишние "off", чтобы их количество соответствовало количеству вопросов
            filtered_right_answers = []
            off_count = 0  # Счетчик "off" в начале списка

            # Пропускаем лишние "off" в начале
            for answer in right_answers:
                if answer == 'off' and off_count < len(right_answers) - len(questions_data):
                    off_count += 1
                else:
                    filtered_right_answers.append(answer)
            # Проверяем, есть ли хотя бы один правильный ответ ("on")
            if not any(answer == 'on' for answer in filtered_right_answers):
                return JsonResponse({
                    "message": "Укажите 1 правильный ответ!",
                    "qwiz_id": qwiz.id,
                    "qwiz_name": qwiz.name
                }, status=400)
            print(f"Right Answers (after filtering): {filtered_right_answers}")

            for i, (question_title, right_answer) in enumerate(zip(questions_data, filtered_right_answers)):
                answer_value = get_right_answer(right_answer)

                # Ищем или создаем вопрос по индексу
                question = Question.objects.filter(qwiz=qwiz).all()[i] if len(
                    Question.objects.filter(qwiz=qwiz).all()) > i else None
                if question:
                    # Если вопрос существует, обновляем его
                    question.title = question_title
                    question.right_answer = answer_value
                    question.description = ""  # Пустое описание
                    question.save()
                else:
                    # Если вопрос не существует, создаем новый
                    Question.objects.create(
                        qwiz=qwiz,
                        title=question_title,
                        right_answer=answer_value,
                        description=""  # Пустое описание
                    )

        elif qwiz_type == 3:  # Тесты с картинками

            questions_data = request.POST.getlist('editqwiz_title_type_3[]')
            right_answers = request.POST.getlist('editqwiz_right_answer_type_3[]')
            images = request.FILES.getlist('image-editqwiz-type-3[]')


            # Получаем существующие вопросы
            existing_questions = list(Question.objects.filter(qwiz=qwiz).order_by('id'))


            # Маппинг имени изображения на id вопроса
            image_to_question_id = {int(re.search(r'image-editqwiz-type-3_(\d+)', img.name).group(1)): img for img in
                                    images}

            for i, question_title in enumerate(questions_data):
                existing_question = existing_questions[i] if i < len(existing_questions) else None


                # Получаем ID существующего вопроса (если есть)
                current_question_id = existing_question.id if existing_question else None

                # Пытаемся найти изображение с соответствующим ID
                current_image = image_to_question_id.get(current_question_id)


                if existing_question:
                    # Обновляем существующий вопрос

                    right_answer_value = 2 if right_answers[i] == "on" else 1
                    existing_question.title = question_title
                    existing_question.right_answer = right_answer_value
                    existing_question.description = ""

                    # Обработка изображения
                    if current_image:
                        if existing_question.image:
                            existing_question.image.delete(save=False)  # Удаляем старое изображение

                        # Формируем имя файла с префиксом и ID вопроса
                        image_name = f"image-editqwiz-type-3_{existing_question.id}.{current_image.name.split('.')[-1]}"

                        # Сохраняем новое изображение с переименованным файлом
                        existing_question.image.save(image_name, ContentFile(current_image.read()), save=True)

                    existing_question.save()

                else:
                    # Создаем новый вопрос
                    print(f"Creating new question for: {question_title}")

                    new_question = Question(
                        qwiz=qwiz,
                        title=question_title,
                        right_answer=right_answers[i],
                        description=""
                    )

                    new_question.save()  # Сначала сохраняем для получения ID

                    # Пытаемся найти изображение для нового вопроса
                    current_image = image_to_question_id.get(new_question.id)

                    if current_image:
                        # Формируем имя файла с префиксом и ID нового вопроса
                        image_name = f"image-editqwiz-type-3_{new_question.id}.{current_image.name.split('.')[-1]}"

                        # Сохраняем изображение с нужным именем
                        new_question.image.save(image_name, ContentFile(current_image.read()), save=True)

                    print(f"Created question ID: {new_question.id}")

        elif qwiz_type == 4:  # Выборка
            questions_data_4_1 = request.POST.getlist('editqwiz_title_type_4_1[]')
            questions_data_4_2 = request.POST.getlist('editqwiz_title_type_4_2[]')
            right_answers = request.POST.getlist('editqwiz_right_answer_type_4_1[]')

            existing_questions = list(Question.objects.filter(qwiz=qwiz).all())
            for i, (question_title_1, question_title_2, right_answer) in enumerate(
                    zip(questions_data_4_1, questions_data_4_2, right_answers)):
                answer_value = int(right_answer) if right_answer in ['1', '2'] else 1
                if i < len(existing_questions):
                    # Если вопрос существует
                    question = existing_questions[i]
                    question.title = question_title_1
                    question.second_title = question_title_2
                    question.right_answer = answer_value
                    question.description = ""
                    question.save()
                else:
                    # Если вопрос не существует
                    Question.objects.create(
                        qwiz=qwiz,
                        title=question_title_1,
                        second_title=question_title_2,
                        right_answer=answer_value,
                        description=""
                    )

        elif qwiz_type == 5:  # Заполните пропуск
            descriptions_data = request.POST.getlist('editqwiz_description_type_5[]')
            print(f"Descriptions: {descriptions_data}")

            # Перебор всех подсказок и их статусов
            hints_data = {}
            statuses_data = {}

            for key in request.POST:
                if key.startswith('hint_'):  # Ищем подсказки по префиксу
                    parts = key.split('_')
                    print(f"hint_ parts: {parts}")
                    # Проверка: ключ должен содержать хотя бы 3 части
                    if len(parts) >= 2 and parts[1].isdigit():
                        question_id = int(parts[1])
                        print(f"hint_ question_id : {question_id}")
                        if question_id not in hints_data:
                            hints_data[question_id] = []
                        hints_data[question_id].extend(request.POST.getlist(key))  # Используем getlist, если это массив
                    else:
                        print(f"Неверный формат ключа: {key}")

                # Обработка статусов правильных ответов для подсказок
                if key.startswith('qwiz_right_answer_type_5_'):  # Ищем статусы правильных ответов
                    parts = key.split('_')
                    print(f" qwiz_right_answer_type_5 parts: {parts}")
                    # Проверка: ключ должен содержать хотя бы 3 части
                    if len(parts) >= 3 and parts[5].isdigit():
                        question_id = int(parts[5])  # Извлекаем ID вопроса
                        print(f"qwiz_right_answer_type_5 question_id : {question_id}")
                        if question_id not in statuses_data:
                            statuses_data[question_id] = []
                        statuses_data[question_id].extend(request.POST.getlist(key))  # Используем getlist для массивов
                    else:
                        print(f"Неверный формат ключа: {key}")

            print(f"Hints: {hints_data}")
            print(f"Statuses: {statuses_data}")

            # Проверяем, что количество подсказок и статусов совпадает
            for question_id in hints_data:
                if len(hints_data[question_id]) != len(statuses_data[question_id]):
                    print(f"Несоответствие количества подсказок и статусов для вопроса {question_id}")

            # Создание вопросов и привязка подсказок
            for idx, description_value in enumerate(descriptions_data):
                if description_value.strip():  # Пропускаем пустые описания
                    question = Question.objects.create(
                        qwiz=qwiz,
                        title="",
                        description=description_value,
                        right_answer=1  # Устанавливаем по умолчанию значение для правильного ответа
                    )
                    print(f"Создан вопрос с описанием: {description_value}")

                    # Создаем и привязываем подсказки к вопросу
                    for hint_idx, hint_name in enumerate(hints_data.get(idx, [])):
                        if hint_name:
                            status = 2 if statuses_data.get(idx, [])[hint_idx] == 'on' else 1
                            hint = HintsToQuestion.objects.create(
                                name=hint_name,
                                right_answer=status
                            )
                            question.hints.add(hint)

                    question.save()
        elif qwiz_type == 6:
            existing_question_ids = [key.split('_')[-1] for key in request.POST.keys() if
                                     key.startswith('qwiz_title_type_6_') and 'new_' not in key]

            for question_id in existing_question_ids:
                question = get_object_or_404(Question, id=question_id, qwiz=qwiz)

                # Левый текст и файл
                left_text = request.POST.get(f"qwiz_title_type_6_{question_id}", "").strip()
                left_file = request.FILES.get(f"image-qwiz-type-6_{question_id}")

                # Правый текст и файл
                right_text = request.POST.get(f"qwiz_title_type_second_6_{question_id}", "").strip()
                right_file = request.FILES.get(f"image-qwiz-type-second-6_{question_id}")

                # Логика для левого блока
                if left_text and not left_file:  # Если текст введён, но файла нет
                    if question.left_file:  # Если файл существовал ранее, удаляем его
                        question.left_file.delete(save=False)
                    question.left_text = left_text
                elif left_file:  # Если загружен файл
                    question.left_file = left_file
                    question.left_text = None  # Очищаем текст

                # Логика для правого блока
                if right_text and not right_file:  # Если текст введён, но файла нет
                    if question.right_file:  # Если файл существовал ранее, удаляем его
                        question.right_file.delete(save=False)
                    question.right_text = right_text
                elif right_file:  # Если загружен файл
                    question.right_file = right_file
                    question.right_text = None  # Очищаем текст

                question.save()

            # Теперь создадим новые вопросы
            new_keys = [key for key in request.POST.keys() if key.startswith("qwiz_title_type_6_new_")]

            for new_key in new_keys:
                new_identifier = new_key.split('_')[-1]  # Получаем "new_X"

                # Левый текст и файл
                left_text = request.POST.get(f"qwiz_title_type_6_new_{new_identifier}", "").strip()
                left_file = request.FILES.get(f"image-qwiz-type-6_new_{new_identifier}")

                # Правый текст и файл
                right_text = request.POST.get(f"qwiz_title_type_second_6_new_{new_identifier}", "").strip()
                right_file = request.FILES.get(f"image-qwiz-type-second-6_new_{new_identifier}")

                # Создание нового вопроса только если есть данные
                if left_text or left_file or right_text or right_file:
                    new_question = Question(
                        qwiz=qwiz,
                        left_text=left_text if left_text else None,
                        right_text=right_text if right_text else None,
                        left_file=left_file if left_file else None,
                        right_file=right_file if right_file else None
                    )
                    new_question.save()

        # Возвращаем успешный ответ
        return JsonResponse({
            "message": "Тест успешно обновлен!",
            "qwiz_id": qwiz.id,
            "qwiz_name": qwiz.name
        }, status=200)


@require_POST
@login_required
def create_comment(request):
    content = request.POST.get('content')
    parent_id = request.POST.get('parent')
    course_id = request.POST.get('course')

    if not content or not course_id:
        return JsonResponse({'status': 'error', 'message': 'Требуется содержание комментария и ID курса'}, status=400)

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Курс не найден'}, status=404)

    parent = None
    if parent_id:
        try:
            parent = Coursecomments.objects.get(id=parent_id)
        except Coursecomments.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Родительский комментарий не найден'}, status=404)

    comment = Coursecomments.objects.create(
        content=content,
        course=course,
        user=request.user,
        parent=parent
    )

    return JsonResponse({
        'status': 'success',
        'id': comment.id,
        'content': comment.content,
        'user': comment.user.username,
        'avatar': comment.user.avatar.url,
        'created': comment.create.strftime('%d/%m/%Y'),
    })


@require_POST
@login_required
def create_reviews(request):
    content = request.POST.get('content')
    estimate = request.POST.get('estimate')
    course_id = request.POST.get('course')

    if not content or not course_id:
        return JsonResponse({'status': 'error', 'message': 'Требуется содержание комментария и ID курса'}, status=400)

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Курс не найден'}, status=404)

    reviews = Courserewievs.objects.create(
        content=content,
        estimate=estimate,
        course=course,
        user=request.user,
    )

    return JsonResponse({
        'status': 'success',
        'id': reviews.id,
        'content': reviews.content,
        'estimate': reviews.estimate,
        'user': reviews.user.username,
        'avatar': reviews.user.avatar.url,
        'created': reviews.create.strftime('%d/%m/%Y'),
    })



# График транляций

class SchedulestreamListView(LoginRequiredMixin, View):
    template_name = 'moderations/schedulestream_list.html'
    paginate_by = 10

    def get_context_data(self, request, form=None):
        schedules = Schedulestream.objects.filter(users=request.user).order_by('-data')

        schedules_by_month = {}
        for schedule in schedules:
            month_year = schedule.data.strftime('%Y-%m')
            if month_year not in schedules_by_month:
                schedules_by_month[month_year] = []
            schedules_by_month[month_year].append(schedule)

        months_list = sorted(schedules_by_month.keys(), reverse=True)

        current_month_year = request.GET.get('month')
        if current_month_year not in months_list:
            current_month_year = months_list[0] if months_list else None

        schedules_for_month = schedules_by_month.get(current_month_year, [])

        paginator = Paginator(schedules_for_month, self.paginate_by)
        page = request.GET.get('page')
        try:
            schedules_page = paginator.page(page)
        except PageNotAnInteger:
            schedules_page = paginator.page(1)
        except EmptyPage:
            schedules_page = paginator.page(paginator.num_pages)

        return {
            'schedules_page': schedules_page,
            'months_list': months_list,
            'current_month_year': current_month_year,
            'schedule_form': form or ScheduleForm(),
        }

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class SchedulestreamEventsView(View):

    def get(self, request, *args, **kwargs):
        schedules = Schedulestream.objects.filter(users=request.user)
        events = []
        for schedule in schedules:
            try:
                event = {
                    'title': schedule.themes.course.name,
                    'time_start': schedule.time_start.isoformat(),
                    'time_end': schedule.time_end.isoformat(),
                    'date': schedule.data.isoformat(),
                    'description': schedule.themes.description,
                }
                # Debug print
                print(f"Event: {event}")
                events.append(event)
            except AttributeError as e:
                print(f"Error processing schedule {schedule.id}: {str(e)}")
                # Optionally, you can still add the event with partial data
                events.append({
                    'title': 'Error: Course name not available',
                    'time_start': schedule.time_start.isoformat(),
                    'time_end': schedule.time_end.isoformat(),
                    'date': schedule.data.isoformat(),
                    'description': 'Error: Description not available',
                })

        return JsonResponse(events, safe=False)


# График
class ScheduleListView(LoginRequiredMixin, View):
    template_name = 'moderations/schedule_list.html'
    paginate_by = 10

    def get_context_data(self, request, form=None):
        schedules = Schedule.objects.filter(user=request.user).order_by('-data')

        schedules_by_month = {}
        for schedule in schedules:
            month_year = schedule.data.strftime('%Y-%m')
            if month_year not in schedules_by_month:
                schedules_by_month[month_year] = []
            schedules_by_month[month_year].append(schedule)

        months_list = sorted(schedules_by_month.keys(), reverse=True)

        current_month_year = request.GET.get('month')
        if current_month_year not in months_list:
            current_month_year = months_list[0] if months_list else None

        schedules_for_month = schedules_by_month.get(current_month_year, [])

        paginator = Paginator(schedules_for_month, self.paginate_by)
        page = request.GET.get('page')
        try:
            schedules_page = paginator.page(page)
        except PageNotAnInteger:
            schedules_page = paginator.page(1)
        except EmptyPage:
            schedules_page = paginator.page(paginator.num_pages)

        return {
            'schedules_page': schedules_page,
            'months_list': months_list,
            'current_month_year': current_month_year,
            'schedule_form': form or ScheduleForm(),
        }

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = ScheduleForm(request.POST)
        if form.is_valid():
            new_schedule = form.save(commit=False)
            new_schedule.user = request.user
            new_schedule.save()
            return redirect('moderation:schedule_list')

        context = self.get_context_data(request, form=form)
        return render(request, self.template_name, context)


class ScheduleDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notebook = get_object_or_404(Schedule, pk=pk)
        if notebook.user == request.user:
            notebook.delete()
            return JsonResponse({'message': 'Notebook deleted successfully'}, status=200)
        else:
            return JsonResponse({'error': 'You do not have permission to delete this notebook'}, status=403)


@method_decorator(login_required, name='dispatch')
class ScheduleEventsView(View):

    def get(self, request, *args, **kwargs):
        schedules = Schedule.objects.filter(user=request.user)
        events = [
            {
                'title': schedule.name,
                'time_start': schedule.time_start.isoformat(),  # Преобразуем в строку
                'time_end': schedule.time_end.isoformat(),  # Преобразуем в строку
                'date': schedule.data.isoformat(),  # Переименовали ключ для ясности
                'description': schedule.description,
            } for schedule in schedules
        ]
        return JsonResponse(events, safe=False)


"""Тайминг"""


# тайминги
def getusersession(request):
    if request.method == 'GET':
        try:
            user_id = request.user.id
            current_url = request.POST.get('current_url')
            user = get_object_or_404(Profile, pk=user_id)
            current_date = timezone.now()
            usbfirst = UserSessionBridge.objects.filter(user=user).first()
            if UserSessionBridge.objects.filter(user=user, url=current_url, ).exists():
                users_session_bridge = UserSessionBridge.objects.get(user=user, url=current_url, )
            else:
                users_session_bridge = UserSessionBridge.objects.create(
                    user=user,
                    url=current_url,
                    date=current_date
                )
            # Обновляем информацию в UserSessionBridge
            if not users_session_bridge.time:
                users_session_bridge.time = 1
            else:
                users_session_bridge.time += 1

            users_session_bridge.save()
            if usbfirst.url != current_url:
                # Создаем новую запись в UserSession
                user_sessionsbridge = UserSessionBridge.objects.filter(
                    user=user
                ).first()

                user_sessions_info = []

                session_info = {
                    "user": user_sessionsbridge.user.username,
                    "url": user_sessionsbridge.url,
                    "time": str(user_sessionsbridge.time),
                    "date": user_sessionsbridge.date
                }
                user_sessions_info.append(session_info)

                if UserSession.objects.filter(user=user, month=current_date.strftime('%B')).exists():
                    usersession = UserSession.objects.get(user=user, month=current_date.strftime('%B'))
                    existing_info = usersession.info
                    updated_info = existing_info + str(user_sessions_info)
                    usersession.info = updated_info
                    usersession.save()
                else:
                    UserSession.objects.create(user=user, info=str(user_sessions_info),
                                               month=current_date.strftime('%B'))
                # Удаляем старую запись из UserSessionBridge
                usballforuser = UserSessionBridge.objects.filter(user=user)
                for item in usballforuser:
                    item.delete()

                # Создаем новую запись в UserSessionBridge с обновленными данными
                users_session_bridge = UserSessionBridge.objects.create(
                    user=user,
                    url=current_url,
                    date=current_date
                )
            return HttpResponse('ok')
        except Exception as e:
            print(e)  # Обработайте ошибку по вашему усмотрению
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return HttpResponse('Method not allowed')


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class UserSessionListView(ListView):
    model = UserSession
    template_name = 'moderations/user_session_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user_moderator_timing'] = user
        if self.request.GET.get('month'):
            month = self.request.GET.get('month')
        else:
            month = 'September'
        user_sessions = UserSession.objects.filter(user=user, month=month)
        user_sessions_all = UserSession.objects.filter(user=user)
        months = []
        for session in user_sessions_all:
            months.append(session.month)
        context['month'] = month
        context['months'] = months

        # Словарь для хранения информации по дням
        # Список для хранения информации по всем сеансам
        daily_sessions = {}
        all_time_in_seconds = 0
        # Обработка данных из поля info без JSON
        for session in user_sessions:
            session_data = [eval(data) for data in session.info.strip('[]').split('][')]
            for data in session_data:
                # Преобразуем строку в объект datetime и извлекаем только дату без времени
                date = datetime.strptime(data.get('date', ''), "%Y-%m-%d %H:%M:%S.%f+00:00").date()
                time = data.get('time', '')
                url = data.get('url', '')
                if time != 'None':
                    all_time_in_seconds += int(time)
                if date not in daily_sessions:
                    daily_sessions[date] = {'total_time': 0, 'sessions': []}
                daily_sessions[date]['sessions'].append((url, time))
                if time != 'None':  # Проверка, что время представлено числом
                    daily_sessions[date]['total_time'] += int(time)
        # Группировка сессий по датам
        grouped_sessions = []
        for day, info in daily_sessions.items():
            total_time_minutes = info['total_time'] // 60  # Делим на 60 для получения времени в минутах
            grouped_sessions.append({'day': str(day), 'sessions': info['sessions'], 'total_time': total_time_minutes})
        # Сортировка по убыванию даты
        grouped_sessions.sort(key=lambda x: datetime.strptime(x['day'], "%Y-%m-%d"), reverse=True)

        context['user_sessions'] = user_sessions
        context['sessions_by_day'] = grouped_sessions
        context['all_time_in_minuts'] = all_time_in_seconds // 60

        return context


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class UserOtherSessionListView(ListView):
    model = UserSession
    template_name = 'moderations/user_session_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs['moderator_id']
        user = get_object_or_404(Profile, pk=user_id)
        context['user_moderator_timing'] = user
        if self.request.GET.get('month'):
            month = self.request.GET.get('month')
        else:
            month = 'August'
        user_sessions = UserSession.objects.filter(user=user, month=month)
        user_sessions_all = UserSession.objects.filter(user=user)
        months = []
        for session in user_sessions_all:
            months.append(session.month)
        context['month'] = month
        context['months'] = months
        daily_sessions = {}
        all_time_in_seconds = 0
        # Обработка данных из поля info без JSON
        for session in user_sessions:
            session_data = [eval(data) for data in session.info.strip('[]').split('][')]
            for data in session_data:
                # Преобразуем строку в объект datetime и извлекаем только дату без времени
                date = datetime.strptime(data.get('date', ''), "%Y-%m-%d %H:%M:%S.%f+00:00").date()
                time = data.get('time', '')
                url = data.get('url', '')
                if time != 'None':
                    all_time_in_seconds += int(time)
                if date not in daily_sessions:
                    daily_sessions[date] = {'total_time': 0, 'sessions': []}
                daily_sessions[date]['sessions'].append((url, time))
                if time != 'None':  # Проверка, что время представлено числом
                    daily_sessions[date]['total_time'] += int(time)
        # Группировка сессий по датам
        grouped_sessions = []
        for day, info in daily_sessions.items():
            total_time_minutes = info['total_time'] // 60  # Делим на 60 для получения времени в минутах
            grouped_sessions.append({'day': str(day), 'sessions': info['sessions'], 'total_time': total_time_minutes})
        # Сортировка по убыванию даты
        grouped_sessions.sort(key=lambda x: datetime.strptime(x['day'], "%Y-%m-%d"), reverse=True)

        context['user_sessions'] = user_sessions
        context['sessionss_by_day'] = grouped_sessions
        context['grouped_sessions'] = grouped_sessions
        context['all_time_in_minutes'] = all_time_in_seconds // 60

        return context



class SettingGlobalUpdateView(UpdateView, LoginRequiredMixin):
    model = SettingsGlobale
    form_class = SettingsGlobaleForm
    template_name = 'moderations/settings_global.html'
    context_object_name = 'site'
    success_url = reverse_lazy('moderation:settings_global')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        else:
            return response

    def get_object(self, queryset=None):
        return SettingsGlobale.objects.first()


def create_testimonial(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        testimonial = Testimonial.objects.create(
            name=name,
            description=description,
            image=image,
        )

        return JsonResponse({'success': True, 'testimonial_id': testimonial.id})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


class ContactUpdateView(UpdateView, LoginRequiredMixin):
    model = ContactPage
    form_class = ContactPageForm
    template_name = 'moderations/contactpageform.html'
    context_object_name = 'contactpage'
    success_url = reverse_lazy('moderation:contact_update')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):

        response = super().form_valid(form)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        else:
            return response

    def get_object(self, queryset=None):
        return ContactPage.objects.first()


class FaqSettings(ListView, LoginRequiredMixin):
    template_name = 'moderations/faqs_settings.html'
    model = Faqs
    context_object_name = 'faqs_settings'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faq = Faqs.objects.order_by('-create').all()

        search_id = self.request.GET.get('search_id', '')
        if search_id:
            faq = faq.filter(pk=search_id)

        search_name = self.request.GET.get('search_name', '')
        if search_name:
            faq = faq.filter(question__icontains=search_name)

        search_date = self.request.GET.get('search_date', '')
        if search_date:
            # Преобразуем строку даты в объект datetime
            try:
                search_date = timezone.datetime.strptime(search_date, '%Y-%m-%d').date()
                faq = faq.filter(create__date=search_date)
            except ValueError:
                pass

        # Пагинация
        paginator = Paginator(faq, 10)  # 20 элементов на страницу
        page = self.request.GET.get('page')
        try:
            faq_list = paginator.page(page)
        except PageNotAnInteger:
            faq_list = paginator.page(1)
        except EmptyPage:
            faq_list = paginator.page(paginator.num_pages)

        context['faq_list'] = faq_list  # Передаем отфильтрованные задачи
        context['paginator'] = paginator
        context['page_obj'] = faq_list
        return context


class FaqCreateView(CreateView, LoginRequiredMixin):
    model = Faqs
    form_class = FaqsForm
    template_name = 'moderations/faqs_form.html'
    success_url = reverse_lazy('moderation:faq_settings')
    context_object_name = 'faqs'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class FaqUpdateView(UpdateView, LoginRequiredMixin):
    model = Faqs
    form_class = FaqsForm
    template_name = 'moderations/faqs_form.html'
    success_url = reverse_lazy('moderation:faq_settings')
    context_object_name = 'faqs'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class FaqDeleteView(View, LoginRequiredMixin):
    success_url = reverse_lazy('moderation:faq_settings')

    def post(self, request):
        data = json.loads(request.body)
        faq_ids = data.get('faq_ids', [])
        if faq_ids:
            Faqs.objects.filter(id__in=faq_ids).delete()
        return JsonResponse({'status': 'success', 'redirect': self.success_url})


class BlogsSettings(ListView, LoginRequiredMixin):
    template_name = 'moderations/blogs_settings.html'
    model = Blogs
    context_object_name = 'blogs_settings'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blogs = Blogs.objects.all()
        context['categories'] = Categorys.objects.all()

        search_name = self.request.GET.get('search_name', '')
        if search_name:
            blogs = blogs.filter(name__icontains=search_name)

        search_date = self.request.GET.get('search_date', '')
        if search_date:
            # Преобразуем строку даты в объект datetime
            try:
                search_date = timezone.datetime.strptime(search_date, '%Y-%m-%d').date()
                blogs = blogs.filter(create__date=search_date)
            except ValueError:
                pass

        search_category = self.request.GET.get('search_category', '')
        if search_category:
            blogs = blogs.filter(category__id=search_category)

        # Пагинация
        paginator = Paginator(blogs, 10)  # 20 элементов на страницу
        page = self.request.GET.get('page')
        try:
            blogs_list = paginator.page(page)
        except PageNotAnInteger:
            blogs_list = paginator.page(1)
        except EmptyPage:
            blogs_list = paginator.page(paginator.num_pages)

        context['blogs_list'] = blogs_list  # Передаем отфильтрованные задачи
        context['paginator'] = paginator
        context['page_obj'] = blogs_list
        return context


class BlogCreateView(CreateView, LoginRequiredMixin):
    model = Blogs
    form_class = BlogsForm
    template_name = 'moderations/blogs_form.html'
    success_url = reverse_lazy('moderation:blog_settings')
    context_object_name = 'blogs'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Categorys.objects.all()
        return context

    def form_valid(self, form):
        blogs = form.save()
        category = self.request.POST.getlist('category')

        if category:
            blogs.category.clear()
            for category_id in category:
                category = get_object_or_404(Categorys, id=category_id)
                blogs.category.add(category)

        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)  # Это поможет вам увидеть ошибки валидации
        return super().form_invalid(form)


class BlogUpdateView(UpdateView, LoginRequiredMixin):
    model = Blogs
    form_class = BlogsForm
    template_name = 'moderations/blogs_form.html'
    success_url = reverse_lazy('moderation:blog_settings')
    context_object_name = 'blogs'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Categorys.objects.all()
        context['categories'] = categories

        return context

    def form_valid(self, form):
        blogs = form.save()
        category = self.request.POST.getlist('category')

        if category:
            blogs.category.clear()
            for category_id in category:
                category = get_object_or_404(Categorys, id=category_id)
                blogs.category.add(category)

        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)  # Это поможет вам увидеть ошибки валидации
        return super().form_invalid(form)


class BlogDeleteView(View, LoginRequiredMixin):
    success_url = reverse_lazy('moderation:blog_settings')

    def post(self, request):
        data = json.loads(request.body)
        blogs_ids = data.get('blogs_ids', [])
        if blogs_ids:
            Blogs.objects.filter(id__in=blogs_ids).delete()
        return JsonResponse({'status': 'success', 'redirect': self.success_url})


@login_required()
def save_categories(request, slug):
    # Получаем объект блога по slug
    blog = get_object_or_404(Blogs, slug=slug)

    if request.method == 'GET':
        categories = request.GET.get('categories', '')
        if categories:
            category_list = categories.split(',')
            blog.category.clear()
            for category_id in category_list:
                category = get_object_or_404(Categorys, id=category_id)
                blog.category.add(category)

            return JsonResponse({'status': 'success', 'message': 'Categories saved successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'No categories provided.'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


@login_required()
def create_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        title = request.POST.get('title')
        content = request.POST.get('content')
        parent_id = request.POST.get('parent')
        cover = request.FILES.get('cover')
        icon = request.FILES.get('icon')
        image = request.FILES.get('image')
        site_id = request.POST.get('site')

        category = Categorys.objects.create(
            name=name,
            slug=slug,
            description=description,
            title=title,
            content=content,
            parent_id=parent_id,
            cover=cover,
            icon=icon,
            image=image,
            site_id=1,
        )

        return JsonResponse({'success': True, 'category_id': category.id})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


def category_list(request):
    categories = Categorys.objects.all().values('id', 'name')  # Получаем нужные поля
    return JsonResponse({'categories': list(categories)})


class PagesSettings(ListView, LoginRequiredMixin):
    template_name = 'moderations/pages_settings.html'
    model = Pages
    context_object_name = 'pages_settings'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pages = Pages.objects.all()
        context['pagetypes'] = Pages.PAGETYPE

        search_name = self.request.GET.get('search_name', '')
        if search_name:
            pages = pages.filter(name__icontains=search_name)

        search_id = self.request.GET.get('search_id', '')
        if search_id:
            pages = pages.filter(slug__icontains=search_id)

        search_type = self.request.GET.get('search_type', '')
        if search_type:
            pages = pages.filter(pagetype=search_type)

        # Пагинация
        paginator = Paginator(pages, 10)  # 20 элементов на страницу
        page = self.request.GET.get('page')
        try:
            pages_list = paginator.page(page)
        except PageNotAnInteger:
            pages_list = paginator.page(1)
        except EmptyPage:
            pages_list = paginator.page(paginator.num_pages)

        context['pages_list'] = pages_list  # Передаем отфильтрованные задачи
        context['paginator'] = paginator
        context['page_obj'] = pages_list
        return context


class PagesCreateView(CreateView, LoginRequiredMixin):
    model = Pages
    form_class = PagesForm
    template_name = 'moderations/pages_form.html'
    success_url = reverse_lazy('moderation:pages_settings')
    context_object_name = 'pages'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class PagesUpdateView(UpdateView, LoginRequiredMixin):
    model = Pages
    form_class = PagesForm
    template_name = 'moderations/pages_form.html'
    success_url = reverse_lazy('moderation:pages_settings')
    context_object_name = 'pages'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class PagesDeleteView(View, LoginRequiredMixin):
    success_url = reverse_lazy('moderation:pages_settings')

    def post(self, request):
        data = json.loads(request.body)
        pages_ids = data.get('pages_ids', [])
        if pages_ids:
            Pages.objects.filter(id__in=pages_ids).delete()
        return JsonResponse({'status': 'success', 'redirect': self.success_url})


class JobsSettings(ListView, LoginRequiredMixin):
    template_name = 'moderations/jobs_settings.html'
    model = Jobs
    context_object_name = 'jobs_settings'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pages = Jobs.objects.all()

        search_name = self.request.GET.get('search_name', '')
        if search_name:
            pages = pages.filter(name__icontains=search_name)

        search_id = self.request.GET.get('search_id', '')
        if search_id:
            pages = pages.filter(slug__icontains=search_id)

        # Пагинация
        paginator = Paginator(pages, 10)  # 20 элементов на страницу
        page = self.request.GET.get('page')
        try:
            pages_list = paginator.page(page)
        except PageNotAnInteger:
            pages_list = paginator.page(1)
        except EmptyPage:
            pages_list = paginator.page(paginator.num_pages)

        context['pages_list'] = pages_list  # Передаем отфильтрованные задачи
        context['paginator'] = paginator
        context['page_obj'] = pages_list
        return context


class JobsCreateView(CreateView, LoginRequiredMixin):
    model = Jobs
    form_class = JobsForm
    template_name = 'moderations/jobs_form.html'
    success_url = reverse_lazy('moderation:jobs_settings')
    context_object_name = 'pages'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class JobsUpdateView(UpdateView, LoginRequiredMixin):
    model = Jobs
    form_class = JobsForm
    template_name = 'moderations/jobs_form.html'
    success_url = reverse_lazy('moderation:jobs_settings')
    context_object_name = 'pages'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class JobsDeleteView(View, LoginRequiredMixin):
    success_url = reverse_lazy('moderation:jobs_settings')

    def post(self, request):
        data = json.loads(request.body)
        pages_ids = data.get('pages_ids', [])
        if pages_ids:
            Jobs.objects.filter(id__in=pages_ids).delete()
        return JsonResponse({'status': 'success', 'redirect': self.success_url})


class LandingListView(ListView):
    model = Landing
    template_name = 'moderations/landing_list.html'
    context_object_name = 'landings'


class LandingCreateView(CreateView):
    model = Landing
    template_name = 'moderations/landing_form.html'
    fields = ['title', 'slug']
    success_url = reverse_lazy('moderation:landing_list')

    def form_valid(self, form):
        messages.success(self.request, 'Лендинг успешно создан')
        return super().form_valid(form)


class LandingEditorView(UpdateView):
    model = Landing
    template_name = 'moderations/landing_form.html'
    fields = ['title', 'html_content', 'css_content', 'is_published']

    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug')
        if slug:
            return get_object_or_404(Landing, slug=slug)
        return None


@method_decorator(csrf_exempt, name='dispatch')
class SaveLandingView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            slug = data.get('slug')

            if not slug:
                return JsonResponse({
                    'success': False,
                    'error': 'Slug is required'
                }, status=400)

            landing = get_object_or_404(Landing, slug=slug)

            # Обновляем содержимое
            landing.html_content = data.get('html', landing.html_content)
            landing.css_content = data.get('css', landing.css_content)
            landing.save()

            return JsonResponse({
                'success': True,
                'message': 'Landing page saved successfully'
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Landing.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Landing page not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class NeedcourseSettings(ListView, LoginRequiredMixin):
    template_name = 'moderations/needcourse_settings.html'
    model = Needcourse
    context_object_name = 'needcourse_settings'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pages = Jobs.objects.all()

        search_name = self.request.GET.get('search_name', '')
        if search_name:
            pages = pages.filter(name__icontains=search_name)

        search_id = self.request.GET.get('search_id', '')
        if search_id:
            pages = pages.filter(slug__icontains=search_id)

        # Пагинация
        paginator = Paginator(pages, 10)  # 20 элементов на страницу
        page = self.request.GET.get('page')
        try:
            pages_list = paginator.page(page)
        except PageNotAnInteger:
            pages_list = paginator.page(1)
        except EmptyPage:
            pages_list = paginator.page(paginator.num_pages)

        context['pages_list'] = pages_list  # Передаем отфильтрованные задачи
        context['paginator'] = paginator
        context['page_obj'] = pages_list
        return context


class NeedcourseCreateView(CreateView, LoginRequiredMixin):
    model = Needcourse
    form_class = NeedcourseForm
    template_name = 'moderations/needcourse_form.html'
    success_url = reverse_lazy('moderation:needcourse_settings')
    context_object_name = 'pages'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class NeedcourseUpdateView(UpdateView, LoginRequiredMixin):
    model = Needcourse
    form_class = NeedcourseForm
    template_name = 'moderations/needcourse_form.html'
    success_url = reverse_lazy('moderation:needcourse_settings')
    context_object_name = 'pages'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class NeedcourseDeleteView(View, LoginRequiredMixin):
    success_url = reverse_lazy('moderation:needcourse_settings')

    def post(self, request):
        data = json.loads(request.body)
        pages_ids = data.get('pages_ids', [])
        if pages_ids:
            Jobs.objects.filter(id__in=pages_ids).delete()
        return JsonResponse({'status': 'success', 'redirect': self.success_url})


class OrganizationsSettings(ListView, LoginRequiredMixin):
    template_name = 'moderations/organizations_settings.html'
    model = Organizations
    context_object_name = 'organizations_settings'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pages = Jobs.objects.all()

        search_name = self.request.GET.get('search_name', '')
        if search_name:
            pages = pages.filter(name__icontains=search_name)

        search_id = self.request.GET.get('search_id', '')
        if search_id:
            pages = pages.filter(slug__icontains=search_id)

        # Пагинация
        paginator = Paginator(pages, 10)  # 20 элементов на страницу
        page = self.request.GET.get('page')
        try:
            pages_list = paginator.page(page)
        except PageNotAnInteger:
            pages_list = paginator.page(1)
        except EmptyPage:
            pages_list = paginator.page(paginator.num_pages)

        context['pages_list'] = pages_list  # Передаем отфильтрованные задачи
        context['paginator'] = paginator
        context['page_obj'] = pages_list
        return context


class OrganizationsCreateView(CreateView, LoginRequiredMixin):
    model = Organizations
    form_class = OrganizationsForm
    template_name = 'moderations/organizations_form.html'
    success_url = reverse_lazy('moderation:organizations_settings')
    context_object_name = 'pages'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class OrganizationsUpdateView(UpdateView, LoginRequiredMixin):
    model = Organizations
    form_class = OrganizationsForm
    template_name = 'moderations/organizations_form.html'
    success_url = reverse_lazy('moderation:organizations_settings')
    context_object_name = 'pages'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class OrganizationsDeleteView(View, LoginRequiredMixin):
    success_url = reverse_lazy('moderation:organizations_settings')

    def post(self, request):
        data = json.loads(request.body)
        pages_ids = data.get('pages_ids', [])
        if pages_ids:
            Jobs.objects.filter(id__in=pages_ids).delete()
        return JsonResponse({'status': 'success', 'redirect': self.success_url})


class SeoSettings(ListView, LoginRequiredMixin):
    template_name = 'moderations/seosettings.html'
    model = Seo
    context_object_name = 'seo_settings'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seo = Seo.objects.all()
        context['pagetypes'] = Seo.PAGE_CHOICE

        search_name = self.request.GET.get('search_name', '')
        if search_name:
            seo = seo.filter(title__icontains=search_name)

        search_id = self.request.GET.get('search_id', '')
        if search_id:
            seo = seo.filter(pk=search_id)

        search_type = self.request.GET.get('search_type', '')
        if search_type:
            seo = seo.filter(pagetype=search_type)

        # Пагинация
        paginator = Paginator(seo, 10)  # 20 элементов на страницу
        page = self.request.GET.get('page')
        try:
            seo_list = paginator.page(page)
        except PageNotAnInteger:
            seo_list = paginator.page(1)
        except EmptyPage:
            seo_list = paginator.page(paginator.num_pages)

        context['seo_list'] = seo_list  # Передаем отфильтрованные задачи
        context['paginator'] = paginator
        context['page_obj'] = seo_list
        return context


class SeoCreateView(CreateView, LoginRequiredMixin):
    model = Seo
    form_class = SeoForm
    template_name = 'moderations/seoform.html'
    success_url = reverse_lazy('moderation:seo_settings')
    context_object_name = 'seo'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class SeoUpdateView(UpdateView, LoginRequiredMixin):
    model = Seo
    form_class = SeoForm
    template_name = 'moderations/seoform.html'
    success_url = reverse_lazy('moderation:seo_settings')
    context_object_name = 'seo'

    def form_valid(self, form):
        form.instance.setting = SettingsGlobale.objects.first()
        form.save()
        return super().form_valid(form)


class SeoDeleteView(LoginRequiredMixin, View):
    success_url = reverse_lazy('moderation:seo_settings')

    def post(self, request, seo_id):
        seo = get_object_or_404(Seo, pk=seo_id)
        seo.delete()
        return redirect('moderation:seo_settings')


class SeoDeleteMultipleView(LoginRequiredMixin, View):
    success_url = reverse_lazy('moderation:seo_settings')

    def post(self, request):
        data = json.loads(request.body)
        seo_ids = data.get('seo_ids', [])
        if seo_ids:
            Seo.objects.filter(id__in=seo_ids).delete()
        return JsonResponse({'status': 'success', 'redirect': self.success_url})


class NotificationSettings(ListView, LoginRequiredMixin):
    template_name = 'moderations/notifications_settings.html'
    model = Notificationgroups
    context_object_name = 'notification_settings'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notifications = Notificationgroups.objects.all()
        context['content_types'] = ContentType.objects.all()
        context['users'] = get_user_model().objects.all()

        search_id = self.request.GET.get('search_id', '')
        if search_id:
            notifications = notifications.filter(object_id=search_id)

        search_type = self.request.GET.get('search_type', '')
        if search_type:
            notifications = notifications.filter(content_type=search_type)

        search_date = self.request.GET.get('search_date', '')
        if search_date:
            # Преобразуем строку даты в объект datetime
            try:
                search_date = timezone.datetime.strptime(search_date, '%Y-%m-%d').date()
                notifications = notifications.filter(created_at__date=search_date)
            except ValueError:
                pass

        paginator = Paginator(notifications, 10)
        page = self.request.GET.get('page')
        try:
            notifications_list = paginator.page(page)
        except PageNotAnInteger:
            notifications_list = paginator.page(1)
        except EmptyPage:
            notifications_list = paginator.page(paginator.num_pages)

        context['notifications_list'] = notifications_list
        context['paginator'] = paginator
        context['page_obj'] = notifications_list
        return context


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class UserNotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'moderations/notifications.html'  # Замените на путь к вашему шаблону
    context_object_name = 'notifications'
    paginate_by = 10  # Количество уведомлений на странице

    def get_queryset(self):
        # Получаем все уведомления пользователя
        queryset = Notification.objects.filter(user=self.request.user).order_by('-created_at')

        # Обновляем статус всех непрочитанных уведомлений
        queryset.filter(status=1).update(status=2)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


class DeleteNotificationView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        notification_id = request.POST.get('notification_id')
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.delete()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Уведомление не найдено'})


class NotificationCreateView(CreateView, LoginRequiredMixin):
    model = Notificationgroups
    form_class = NotificationForm
    template_name = 'moderations/notifications_form.html'
    success_url = reverse_lazy('moderation:notifications_settings')
    context_object_name = 'notifications'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class NotificationDeleteMultipleView(LoginRequiredMixin, View):
    success_url = reverse_lazy('moderation:seo_settings')

    def post(self, request):
        data = json.loads(request.body)
        notification_ids = data.get('notification_ids', [])
        if notification_ids:
            Notificationgroups.objects.filter(id__in=notification_ids).delete()
        return JsonResponse({'status': 'success', 'redirect': self.success_url})


class CategorysSettings(ListView, LoginRequiredMixin):
    template_name = 'moderations/categorys_settings.html'
    model = Categorys
    context_object_name = 'categorys_settings'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categorys = Categorys.objects.all()

        search_name = self.request.GET.get('search_name', '')
        if search_name:
            categorys = categorys.filter(name__icontains=search_name)

        search_category = self.request.GET.get('search_category', '')
        if search_category:
            categorys = categorys.filter(parent__id=search_category)

        # Пагинация
        paginator = Paginator(categorys, 10)  # 20 элементов на страницу
        page = self.request.GET.get('page')
        try:
            categorys_list = paginator.page(page)
        except PageNotAnInteger:
            categorys_list = paginator.page(1)
        except EmptyPage:
            categorys_list = paginator.page(paginator.num_pages)

        context['categorys_list'] = categorys_list  # Передаем отфильтрованные задачи
        context['paginator'] = paginator
        context['page_obj'] = categorys_list
        return context


class CategorysCreateView(CreateView, LoginRequiredMixin):
    model = Categorys
    form_class = CategorysForm
    template_name = 'moderations/categorys_form.html'
    success_url = reverse_lazy('moderation:categorys_settings')
    context_object_name = 'categorys'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class CategorysUpdateView(UpdateView, LoginRequiredMixin):
    model = Categorys
    form_class = CategorysForm
    template_name = 'moderations/categorys_form.html'
    success_url = reverse_lazy('moderation:categorys_settings')
    context_object_name = 'categorys'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class CategorysDeleteView(View, LoginRequiredMixin):
    success_url = reverse_lazy('moderation:categorys_settings')

    def post(self, request):
        data = json.loads(request.body)
        categorys_ids = data.get('categorys_ids', [])
        if categorys_ids:
            Categorys.objects.filter(id__in=categorys_ids).delete()
        return JsonResponse({'status': 'success', 'redirect': self.success_url})


class PaymentSettings(ListView, LoginRequiredMixin):
    template_name = 'moderations/payment_settings.html'
    model = PaymentType
    context_object_name = 'payment_settings'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment = PaymentType.objects.all()
        context['types'] = PaymentType.TYPE

        search_id = self.request.GET.get('search_id', '')
        if search_id:
            payment = payment.filter(shop_key__icontains=search_id)

        search_type = self.request.GET.get('search_type', '')
        if search_type:
            payment = payment.filter(type=search_type)

        # Пагинация
        paginator = Paginator(payment, 10)  # 20 элементов на страницу
        page = self.request.GET.get('page')
        try:
            payment_list = paginator.page(page)
        except PageNotAnInteger:
            payment_list = paginator.page(1)
        except EmptyPage:
            payment_list = paginator.page(paginator.num_pages)

        context['payment_list'] = payment_list  # Передаем отфильтрованные задачи
        context['paginator'] = paginator
        context['page_obj'] = payment_list
        return context


class PaymentCreateView(CreateView, LoginRequiredMixin):
    model = PaymentType
    form_class = PaymentTypeForm
    template_name = 'moderations/payment_form.html'
    success_url = reverse_lazy('moderation:payment_settings')
    context_object_name = 'payment'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class PaymentUpdateView(UpdateView, LoginRequiredMixin):
    model = PaymentType
    form_class = PaymentTypeForm
    template_name = 'moderations/payment_form.html'
    success_url = reverse_lazy('moderation:payment_settings')
    context_object_name = 'payment'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class PaymentDeleteView(LoginRequiredMixin, View):
    success_url = reverse_lazy('moderation:seo_settings')

    def post(self, request):
        data = json.loads(request.body)
        payment_ids = data.get('payment_ids', [])
        if payment_ids:
            PaymentType.objects.filter(id__in=payment_ids).delete()
        return JsonResponse({'status': 'success', 'redirect': self.success_url})


class ShopPage(LoginRequiredMixin, TemplateView):
    template_name = 'moderations/template/shop.html'


class SchoolPage(LoginRequiredMixin, TemplateView):
    template_name = 'moderations/template/school.html'


class DashboardModer(LoginRequiredMixin, TemplateView):
    template_name = 'moderations/template/dashboard.html'


"""Тикеты"""


class TicketsView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'moderations/tickets.html'
    context_object_name = 'tickets'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket = Ticket.objects.order_by('-date').all()
        context['statuses'] = Ticket.STATUS_CHOICES
        user = self.request.user

        search_name = self.request.GET.get('search_name', '')
        if search_name:
            ticket = ticket.filter(themas__icontains=search_name)

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
        context['paginator'] = paginator
        context['page_obj'] = ticket_list
        return context


class TicketMessageView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'moderations/tickets_messages.html'
    context_object_name = 'ticket'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket = self.object

        # Get all comments related to the ticket
        comments = TicketComment.objects.filter(ticket=ticket).prefetch_related('media').all()

        # Setup pagination
        paginator = Paginator(comments, 10)  # Show 10 comments per page
        page = self.request.GET.get('page')

        try:
            comments_paginated = paginator.page(page)
        except PageNotAnInteger:
            comments_paginated = paginator.page(1)
        except EmptyPage:
            comments_paginated = paginator.page(paginator.num_pages)

        context['ticket_comments'] = comments_paginated
        context['form'] = TicketCommentForm()
        context['ticket'] = ticket
        context['paginator'] = paginator
        context['page_obj'] = comments_paginated

        try:
            seo_data = Seo.objects.get(pagetype=6)
            context.update({
                'seo_previev': seo_data.previev,
                'seo_title': seo_data.title,
                'seo_description': seo_data.description,
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


class TicketDeleteView(LoginRequiredMixin, View):
    success_url = reverse_lazy('moderation:categorys_settings')

    def post(self, request):
        data = json.loads(request.body)
        ticket_ids = data.get('ticket_ids', [])
        if ticket_ids:
            Ticket.objects.filter(id__in=ticket_ids).delete()
        return JsonResponse({'status': 'success', 'redirect': self.success_url})


class TicketCommentCreateView(LoginRequiredMixin, CreateView):
    model = TicketComment
    form_class = TicketCommentForm

    @transaction.atomic
    def form_valid(self, form):
        ticket_id = self.kwargs['ticket_id']
        ticket = get_object_or_404(Ticket, id=ticket_id)
        comment = form.save(commit=False)
        comment.ticket = ticket
        comment.author = self.request.user
        comment.save()

        files = self.request.FILES.getlist('files')
        for file in files:
            TicketCommentMedia.objects.create(comment=comment, file=file)

        return JsonResponse({
            'status': 'success',
            'comment': {
                'id': comment.id,
                'author': comment.author.username,
                'content': comment.content,
                'date': comment.date.strftime('%Y-%m-%d %H:%M:%S'),
                'files': [{'name': media.file.name, 'url': media.file.url} for media in comment.media.all()]
            }
        })

    def form_invalid(self, form):
        print(form.errors)  # Для отладки
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


"""Пользователь"""


@method_decorator(login_required(login_url='useraccount:edit_profile'), name='dispatch')
class UserListView(ListView):
    model = Profile
    template_name = 'moderations/user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        name_query = self.request.GET.get('q')
        contract_query = self.request.GET.get('contract')

        queryset = Profile.objects.filter(Q(type=0)).exclude(id=self.request.user.id).order_by('id')

        if name_query:
            queryset = queryset.filter(
                Q(first_name__iregex=name_query) |
                Q(last_name__iregex=name_query) |
                Q(middle_name__iregex=name_query)
            )

        return queryset

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('moderations/users_list_partial.html', context, request=self.request)
            return JsonResponse({'html': html})
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = Profile.objects.filter(type=0).count()  # Общее количество пользователей
        return context


@method_decorator(login_required(login_url='moderation:dashboard'), name='dispatch')
class EditWorkerProfileView(UpdateView):
    model = Profile
    form_class = WorkerUpdateProfileForm
    template_name = 'moderations/profile_worker_edit.html'

    def get_object(self, queryset=None):
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(Profile, id=user_id)

    def get_success_url(self):
        return reverse_lazy('moderation:worker_list')

    def get_initial(self):
        initial = super().get_initial()
        if self.object.birthday:
            initial['birthday'] = self.object.birthday.strftime('%Y-%m-%d')
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = self.object
        try:
            seo_data = Seo.objects.get(pagetype=15)
            context.update({
                'seo_previev': seo_data.previev,
                'seo_title': seo_data.title,
                'seo_description': seo_data.description,
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


@method_decorator(login_required(login_url='moderation:dashboard'), name='dispatch')
class SignUpClientView(CreateView):
    form_class = SignUpForm
    template_name = 'moderations/register.html'
    success_url = reverse_lazy('moderation:user_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            seo_data = Seo.objects.get(pagetype=8)
        except Seo.DoesNotExist:
            seo_data = None

        context['seo_previev'] = seo_data.previev if seo_data else None
        context['seo_title'] = seo_data.title if seo_data else None
        context['seo_description'] = seo_data.description if seo_data else None
        context['seo_propertytitle'] = seo_data.propertytitle if seo_data else None
        context['seo_propertydescription'] = seo_data.propertydescription if seo_data else None

        return context


@method_decorator(login_required, name='dispatch')
class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = Profile
    template_name = 'moderations/user_confirm_delete.html'
    success_url = reverse_lazy('moderation:user_list')  # URL для перенаправления после удаления

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return redirect(success_url)


class EditProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'moderations/profile_edit.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        profile_id = kwargs.get('pk')  # Получаем ID профиля из URL
        profile = get_object_or_404(Profile, id=profile_id)

        # Проверяем доступ текущего пользователя к редактированию профиля
        if request.user.is_superuser or request.user == profile.user:
            initial_data = {'birthday': profile.birthday.strftime('%Y-%m-%d') if profile.birthday else None}
            form = UserProfileForm(instance=profile, initial=initial_data)
            context = self.get_context_data(form=form, title='Личные данные', profile=profile)
            return self.render_to_response(context)
        else:
            # Возвращаем ошибку доступа или другую страницу
            return HttpResponseForbidden("У вас нет прав для редактирования этого профиля.")

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        profile_id = kwargs.get('pk')  # Получаем ID профиля из URL
        profile = get_object_or_404(Profile, id=profile_id)

        # Проверяем доступ текущего пользователя к редактированию профиля
        if not (request.user.is_superuser or request.user == profile.user):
            return HttpResponseForbidden("У вас нет прав для редактирования этого профиля.")

        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('useraccount:edit_profiles', pk=profile_id)
        else:
            context = self.get_context_data(form=form, title='Личные данные', profile=profile)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = kwargs.get('profile')
        if profile:
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


"""HTMX"""


class UserListHtmxView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'moderations/htmx/user.html'
    context_object_name = 'users'
    paginate_by = 50

    def get_queryset(self):
        queryset = Profile.objects.filter(type=2)
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(Q(username__icontains=search_query))
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        context = self.get_context_data(object_list=queryset)

        if request.headers.get('HX-Request') == 'true':
            return render(request, 'moderations/htmx/user_list_partial.html', context)
        return super().get(request, *args, **kwargs)





class WithdrawPage(LoginRequiredMixin, TemplateView):
    template_name = 'moderations/withdraw.html'
    model = Withdrawal
    context_object_name = 'withdraw'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        withdraw = Withdrawal.objects.filter(user=user).order_by('-pk')

        search_id = self.request.GET.get('search_id', '')
        if search_id:
            withdraw = withdraw.filter(pk=search_id)

        search_type = self.request.GET.get('search_type', '')
        if search_type:
            withdraw = withdraw.filter(type=search_type)

        user_id = self.request.GET.get('user_id', '')
        if user_id:
            withdraw = withdraw.filter(user__id=user_id)

        search_date = self.request.GET.get('search_date', '')
        if search_date:
            # Преобразуем строку даты в объект datetime
            try:
                search_date = timezone.datetime.strptime(search_date, '%Y-%m-%d').date()
                withdraw = withdraw.filter(create=search_date)
            except ValueError:
                pass

        # Пагинация
        paginator = Paginator(withdraw, 10)  # 20 элементов на страницу
        page = self.request.GET.get('page')
        try:
            withdraw_list = paginator.page(page)
        except PageNotAnInteger:
            withdraw_list = paginator.page(1)
        except EmptyPage:
            withdraw_list = paginator.page(paginator.num_pages)

        context['withdraw_list'] = withdraw_list  # Передаем отфильтрованные задачи
        context['paginator'] = paginator
        context['page_obj'] = withdraw_list
        context['types'] = Withdrawal.TYPE_CHOICES
        context['balance'] = user.balance
        return context


class WithdrawCreateView(CreateView, LoginRequiredMixin):
    model = Withdrawal
    form_class = WithdrawForm
    template_name = 'moderations/iframe/withdraw_form.html'
    success_url = reverse_lazy('moderation:withdraw')
    context_object_name = 'withdraw'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['balance'] = user.balance
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class WithdrawAllPage(LoginRequiredMixin, TemplateView):
    template_name = 'moderations/withdraw.html'
    model = Withdrawal
    context_object_name = 'withdraw'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        withdraw = Withdrawal.objects.order_by('-pk').all()

        search_id = self.request.GET.get('search_id', '')
        if search_id:
            withdraw = withdraw.filter(pk=search_id)

        search_type = self.request.GET.get('search_type', '')
        if search_type:
            withdraw = withdraw.filter(type=search_type)

        user_id = self.request.GET.get('user_id', '')
        if user_id:
            withdraw = withdraw.filter(user__id=user_id)

        search_date = self.request.GET.get('search_date', '')
        if search_date:
            # Преобразуем строку даты в объект datetime
            try:
                search_date = timezone.datetime.strptime(search_date, '%Y-%m-%d').date()
                withdraw = withdraw.filter(create=search_date)
            except ValueError:
                pass

        # Пагинация
        paginator = Paginator(withdraw, 10)  # 20 элементов на страницу
        page = self.request.GET.get('page')
        try:
            withdraw_list = paginator.page(page)
        except PageNotAnInteger:
            withdraw_list = paginator.page(1)
        except EmptyPage:
            withdraw_list = paginator.page(paginator.num_pages)

        context['withdraw_list'] = withdraw_list  # Передаем отфильтрованные задачи
        context['paginator'] = paginator
        context['page_obj'] = withdraw_list
        context['types'] = Withdrawal.TYPE_CHOICES
        context['balance'] = user.balance
        return context


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class CompanyModerationGroups(TemplateView):
    template_name = 'moderations/groups.html'
    model = ModerationGroups
    context_object_name = 'groups'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            seo_data = Seo.objects.get(pagetype=1)
            context['title'] = seo_data.title
            context['description'] = seo_data.description
            context['seo_previev'] = seo_data.previev
            context['seo_title'] = seo_data.meta_title
            context['seo_description'] = seo_data.meta_description
            context['seo_propertytitle'] = seo_data.propertytitle
            context['seo_propertydescription'] = seo_data.propertydescription
        except Seo.DoesNotExist:
            context['seo_previev'] = None
            context['seo_title'] = None
            context['seo_description'] = None
            context['title'] = None
            context['description'] = None
            context['seo_propertytitle'] = None
            context['seo_propertydescription'] = None

        groups = ModerationGroups.objects.all()
        name_filter = self.request.GET.get('name', '')

        # Создаем словарь для отфильтрованных пользователей
        filtered_users = {}
        for group in groups:
            filtered_users[group.id] = group.users.all()

        paginator = Paginator(groups, 20)  # 20 элементов на страницу
        page = self.request.GET.get('page')
        try:
            group_num = paginator.page(page)
        except PageNotAnInteger:
            group_num = paginator.page(1)
        except EmptyPage:
            group_num = paginator.page(paginator.num_pages)

        context['filtered_users'] = filtered_users
        context['paginator'] = paginator
        context['page_obj'] = group_num
        context['groups'] = group_num
        context['group_count'] = groups.count()
        context['group_types_display'] = {
            group.id: group.get_types_display() for group in group_num
        }

        return context


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class ModerationGroupsCreateView(CreateView, ):
    model = ModerationGroups
    form_class = ModerationGroupsForm
    template_name = 'moderations/groups_form.html'
    success_url = reverse_lazy('moderation:groups')
    context_object_name = 'groups'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['users_queryset'] = self.get_users_queryset()
        return kwargs

    def get_users_queryset(self):
        query = self.request.GET.get('q')
        queryset = Profile.objects.filter(type=2).exclude(id=self.request.user.id).order_by('id')
        if query:
            queryset = queryset.filter(username__icontains=query)
        return queryset

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_users'] = Profile.objects.none()  # Пустой QuerySet для новых групп
        context['users'] = self.get_users_queryset()  # Объединенный список пользователей для поиска
        context['update'] = False
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('moderations/group_user_search.html', context)
            return JsonResponse({'html': html})
        return super().render_to_response(context, **response_kwargs)


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class ModerationGroupsUpdateView(UpdateView):
    model = ModerationGroups
    form_class = ModerationGroupsForm
    template_name = 'moderations/groups_form.html'
    success_url = reverse_lazy('moderation:groups')
    context_object_name = 'groups'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['users_queryset'] = self.get_users_queryset()
        return kwargs

    def get_users_queryset(self):
        query = self.request.GET.get('q')
        group = self.object
        selected_users = group.users.all()

        # Получаем QuerySet для фильтрации пользователей, которые не выбраны
        queryset = Profile.objects.filter(type=2).exclude(id=self.request.user.id)

        if query:
            queryset = queryset.filter(username__icontains=query)
        else:
            queryset = queryset.exclude(id__in=selected_users).order_by('-id')[:20]

        # Объединяем результаты выбранных пользователей и оставшихся пользователей
        selected_users_ids = selected_users.values_list('id', flat=True)
        additional_users = queryset.values_list('id', flat=True)

        combined_queryset = Profile.objects.filter(
            id__in=list(selected_users_ids) + list(additional_users)
        ).distinct()

        return combined_queryset

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.users.set(self.request.POST.getlist('users'))
        form.instance.types = self.request.POST.getlist('types')
        form.instance.save()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.object
        context['selected_users'] = group.users.all()  # Выбранные пользователи
        context['users'] = self.get_users_queryset()  # Объединенный список пользователей для поиска
        context['update'] = True
        context['selected_types'] = list(group.types)
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('moderations/group_user_search.html', context)
            return JsonResponse({'html': html})
        return super().render_to_response(context, **response_kwargs)


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class ModerationGroupsDeleteView(View):

    def get(self, request, group_id):
        group = get_object_or_404(ModerationGroups, pk=group_id)
        group.delete()
        return redirect('moderation:groups')


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class WorkerListView(ListView):
    model = Profile
    template_name = 'moderations/worker_list.html'
    context_object_name = 'users'
    paginate_by = 13

    def get_queryset(self):
        query = self.request.GET.get('q')
        queryset = Profile.objects.filter(Q(type=2) | Q(type=1)).exclude(id=self.request.user.id).order_by('id')

        if query:
            queryset = queryset.filter(
                Q(first_name__iregex=query) |
                Q(last_name__iregex=query) |
                Q(middle_name__iregex=query)
            )

        return queryset

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('moderations/worker_list_partial.html', context, request=self.request)
            return JsonResponse({'html': html})
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = Profile.objects.filter(type=2).count()  # Общее количество пользователей
        return context


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class SignUpWorkerView(CreateView):
    form_class = SignUpWorkerForm
    template_name = 'moderations/registerworker.html'
    success_url = reverse_lazy('moderation:worker_list')

    def form_valid(self, form):
        try:
            user = form.save()
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f'Ошибка при регистрации работника: {str(e)}')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            seo_data = Seo.objects.get(pagetype=6)
            context.update({
                'seo_previev': seo_data.previev,
                'seo_title': seo_data.title,
                'seo_description': seo_data.description,
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


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class UserDeleteView(DeleteView):
    model = Profile
    template_name = 'moderations/user_confirm_delete.html'
    success_url = reverse_lazy('moderation:user_list')  # URL для перенаправления после удаления

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        # Добавьте здесь проверку прав доступа, например, что пользователь имеет право удалять профили
        # Пример: только суперпользователь или администраторы могут удалять профили
        if not self.request.user.is_superuser:
            raise PermissionDenied("У вас нет прав для удаления профиля.")
        return obj

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return (redirect(success_url)

                @ method_decorator(login_required(login_url='useraccount:login'), name='dispatch'))


class WorkerDeleteView(DeleteView):
    model = Profile
    template_name = 'moderations/user_confirm_delete.html'
    success_url = reverse_lazy('moderation:worker_list')  # URL для перенаправления после удаления

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        # Добавьте здесь проверку прав доступа, например, что пользователь имеет право удалять профили
        # Пример: только суперпользователь или администраторы могут удалять профили
        if not self.request.user.is_superuser:
            raise PermissionDenied("У вас нет прав для удаления профиля.")
        return obj

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return redirect(success_url)


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class UnblockUserView(View):
    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = get_object_or_404(Profile, pk=user_id)
        user.blocked = False
        user.save()

        # Получаем предыдущий URL из заголовка HTTP_REFERER
        previous_url = request.META.get('HTTP_REFERER', 'moderation:user_list')
        return HttpResponseRedirect(previous_url)


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class RestoreUserView(View):
    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = get_object_or_404(Profile, pk=user_id)
        user.deleted = False
        user.save()

        # Получаем предыдущий URL из заголовка HTTP_REFERER
        previous_url = request.META.get('HTTP_REFERER', 'moderation:user_list')
        return HttpResponseRedirect(previous_url)


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class DeleteUserView(View):
    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = get_object_or_404(Profile, pk=user_id)
        user.deleted = True
        user.save()

        # Получаем предыдущий URL из заголовка HTTP_REFERER
        previous_url = request.META.get('HTTP_REFERER', 'moderation:user_list')
        return HttpResponseRedirect(previous_url)


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class BlockUserView(View):
    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = get_object_or_404(Profile, pk=user_id)
        user.blocked = True
        user.save()

        # Получаем предыдущий URL из заголовка HTTP_REFERER
        previous_url = request.META.get('HTTP_REFERER', 'moderation:user_list')
        return HttpResponseRedirect(previous_url)


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class UserDetailView(TemplateView):
    template_name = 'moderations/users_detail.html'

    def get_context_data(self, user_id, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(Profile, id=user_id)
        context['users'] = user
        return context


@csrf_exempt
def tinymce_image_upload(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            # Генерируем уникальное имя
            ext = file.name.split('.')[-1]
            filename = f"{uuid.uuid4()}.{ext}"

            # Создаем путь для сохранения
            upload_path = os.path.join(settings.MEDIA_ROOT, 'tinymce')
            os.makedirs(upload_path, exist_ok=True)

            # Полный путь к файлу
            full_path = os.path.join(upload_path, filename)

            # Сохраняем файл
            with open(full_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Возвращаем URL
            return JsonResponse({
                'location': f"{settings.MEDIA_URL}tinymce/{filename}"
            })

        return JsonResponse({'error': 'No file'}, status=400)

    return JsonResponse({'error': 'Invalid method'}, status=405)

def get_modules(request):
    # Загрузка модулей из базы данных

    user = request.user
    courses = Course.objects.filter(
        Q(author=user) | Q(assistants=user)
    )

    modules = []
    for course in courses:
        try:
            modules = Modules.objects.filter(course=course).order_by('-id')
            for module in modules:
                modules.append(module)
        except:pass
    current_course_content = Course.objects.get(id=request.GET.get('course_id'))
    # Рендеринг шаблона с модулями
    return render(request, 'moderations/courses/watch-library.html', {'modules': modules,'current_course_content':current_course_content})

@csrf_exempt
def libraryupdates(request):
    if request.method == 'POST':
        # Получение данных из POST-запроса
        test_id = request.POST.get('test_id')
        lection_for_qwiz_id = request.POST.get('lection_for_qwiz_id')
        lection_id = request.POST.get('addlection_id')
        module_id = request.POST.get('module_id')
        addtolectiontests = request.POST.get('addtolectiontests')
        addtomodulelection = request.POST.get('addtomodulelection')
        addtomoduletests = request.POST.get('addtomoduletests')

        add_module = request.POST.get('add_module')
        new_name = request.POST.get('new_name')

        if test_id:  # Обработка теста
            return handle_test_creation(test_id, lection_for_qwiz_id, new_name)

        elif lection_id:  # Обработка лекции
            return handle_lection_creation(lection_id, module_id, addtolectiontests, new_name)
        elif add_module:  # Обработка модуль
            return handle_module_creation(add_module, addtomodulelection, addtomoduletests, new_name)
        return JsonResponse({'status': 'error', 'message': 'Неверные данные.'})
    return JsonResponse({'status': 'error', 'message': 'Метод запроса должен быть POST.'})


def handle_test_creation(test_id, lection_for_qwiz_id, new_name):
    """Обработка создания копии теста и привязка его к лекции"""
    try:
        qwiz = Qwiz.objects.get(id=test_id)
        lection = Themes.objects.get(id=lection_for_qwiz_id)
        name = new_name or qwiz.name

        # Создаем копию теста
        new_qwiz = Qwiz.objects.create(
            type=qwiz.type,
            themes=lection,  # Привязываем к указанной лекции
            name=name,
            description=qwiz.description,
            position=qwiz.position,
            point=qwiz.point
        )

        # Копируем вопросы
        for question in qwiz.question_quiz.all():
            Question.objects.create(
                qwiz=new_qwiz,  # Связываем с новой копией теста
                right_answer=question.right_answer,
                title=question.title,
                second_title=question.second_title,
                image=question.image,  # Копируем ссылку на изображение
                description=question.description
            )

        return JsonResponse({'status': 'success',
                             'message': f'Копия теста "{qwiz.name}" успешно добавлена в лекцию {lection.name}.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Ошибка при создании теста: {str(e)}'})


def handle_lection_creation(lection_id, module_id, addtolectiontests, new_name):
    """Обработка создания лекции и, при необходимости, копирование тестов и вопросов"""
    try:
        lection = Themes.objects.get(id=lection_id)
        module = Modules.objects.get(id=module_id)
        name = new_name or lection.name

        # Создаем новую лекцию
        new_lection = Themes.objects.create(
            course=module.course,
            modules=module,
            name=name,
            description=lection.description,
            position=lection.position,
            point=lection.point,
            point_status=lection.point_status,
            attempts=lection.attempts,
            attempts_status=lection.attempts_status,
            test_duration=lection.test_duration,
            access_type=lection.access_type,
            show_answer=lection.show_answer,
            home_work=lection.home_work,
            home_work_status=lection.home_work_status
        )
        # Если нужно добавить тесты и вопросы
        if addtolectiontests == 'on':
            for qwiz in lection.quizzes.all():
                new_qwiz = Qwiz.objects.create(
                    type=qwiz.type,
                    themes=new_lection,  # Привязываем к новой лекции
                    name=f"{qwiz.name}",
                    description=qwiz.description,
                    position=qwiz.position,
                    point=qwiz.point
                )
                # Копируем вопросы
                for question in qwiz.question_quiz.all():
                    Question.objects.create(
                        qwiz=new_qwiz,
                        right_answer=question.right_answer,
                        title=question.title,
                        second_title=question.second_title,
                        image=question.image,
                        description=question.description
                    )

        return JsonResponse({'status': 'success',
                             'message': f'Лекция "{new_lection.name}" успешно создана и привязана к модулю "{module.name}".'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Ошибка при создании лекции: {str(e)}'})

def handle_module_creation(add_module, addtomodulection, addtomoduletests, new_name):
    """Обработка создания нового модуля и привязка лекций и тестов, если необходимо"""
    try:
        # Получаем существующий модуль
        module = Modules.objects.get(id=add_module)
        name = new_name or module.name  # Если новое имя не указано, используем старое

        # Создаем новый модуль
        new_module = Modules.objects.create(
            name=name,
            course=module.course,  # Привязываем к тому же курсу
            position=module.position
        )

        # Если нужно копировать лекции
        if addtomodulection == 'on':
            for lection in module.modulescourse.all():
                new_lection = Themes.objects.create(
                    course=lection.course,
                    modules=new_module,  # Привязываем к новому модулю
                    name=f"{lection.name}",
                    description=lection.description,
                    position=lection.position,
                    point=lection.point,
                    point_status=lection.point_status,
                    attempts=lection.attempts,
                    attempts_status=lection.attempts_status,
                    test_duration=lection.test_duration,
                    access_type=lection.access_type,
                    show_answer=lection.show_answer,
                    home_work=lection.home_work,
                    home_work_status=lection.home_work_status
                )

                # Если нужно копировать тесты для лекции
                if addtomoduletests == 'on' and addtomodulection == 'on':
                    for qwiz in lection.quizzes.all():
                        new_qwiz = Qwiz.objects.create(
                            type=qwiz.type,
                            themes=new_lection,  # Привязываем к новой лекции
                            name=f"{qwiz.name}",
                            description=qwiz.description,
                            position=qwiz.position,
                            point=qwiz.point
                        )
                        # Копируем вопросы
                        for question in qwiz.question_quiz.all():
                            Question.objects.create(
                                qwiz=new_qwiz,
                                right_answer=question.right_answer,
                                title=question.title,
                                second_title=question.second_title,
                                image=question.image,
                                description=question.description
                            )

        return JsonResponse({'status': 'success',
                             'message': f'Модуль "{new_module.name}" успешно создан и лекции/тесты добавлены в зависимости от флагов.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Ошибка при создании модуля: {str(e)}'})

@csrf_exempt
def delete_hint(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        hint_id = data.get('hint_id')

        hint = HintsToQuestion.objects.get(id=hint_id)

        hint.delete()
        return JsonResponse({'status': 'success',
                             'message': f'Подсказка удалена'})
    return JsonResponse({'status': 'error', 'message': f'Ошибка при создании модуля: Метод запроса не поддерживается'})

@csrf_exempt
def delete_question_type_six(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question_id = data.get('questionId')
        question = Question.objects.get(id=question_id)

        question.delete()
        return JsonResponse({'status': 'success',
                             'message': f'Вопрос удален'})
    return JsonResponse({'status': 'error', 'message': f'Ошибка при удалении вопроса: Метод запроса не поддерживается'})

class QuizCompleteView(TemplateView):
    template_name = 'moderations/courses/quizcomplete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        theme_id = kwargs['theme_id']
        user = self.request.user

        theme = Themes.objects.get(id=theme_id)
        theme_control = ThemesQuestion.objects.filter(themes=theme,user=user).last()
        qwiz_count = Qwiz.objects.filter(themes=theme).count()
        max_score = Qwiz.objects.filter(themes=theme).aggregate(total_points=Sum('point'))['total_points'] or 0
        context['theme_control'] = theme_control
        context['course'] = theme.course
        context['theme'] = theme
        context['qwiz_count'] = qwiz_count
        context['max_score'] = max_score
        return context

class NotebookListView(LoginRequiredMixin, View):
    template_name = 'moderations/notebook_list.html'
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

class NotebookDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notebook = get_object_or_404(Notebook, pk=pk)
        if notebook.user == request.user:
            notebook.delete()
            return JsonResponse({'message': 'Notebook deleted successfully'}, status=200)
        else:
            return JsonResponse({'error': 'You do not have permission to delete this notebook'}, status=403)