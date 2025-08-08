from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.views.generic.base import View
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import logout
from django.urls import reverse
from django.http import HttpRequest
from django.contrib.sitemaps.views import sitemap as django_sitemap
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.sitemaps import views as sitemap_views
from django.http import Http404
from django.contrib.sites.models import Site
from django.shortcuts import redirect
from django.contrib.auth import get_user_model, login
from django.utils.crypto import get_random_string
from moderation.forms import ApplicationForm
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

try:
    from _project.domainsmixin import DomainTemplateMixin
except ImportError:
    # Создаем заглушку для DomainTemplateMixin
    class DomainTemplateMixin:
        pass


# Models
from moderation.models import Applications
from useraccount.models import Profile, History
from webmain.models import Faqs, SettingsGlobale, ContactPage,  Testimonial, Seo, Pages, Categorys, Blogs, DocumentationsSite

# Forms


class FirstSiteMixin:
    def dispatch(self, request, *args, **kwargs):
        try:
            current_site = Site.objects.get(domain=request.get_host())
            site_id = current_site.id
        except Site.DoesNotExist:
            raise Http404("Страница не найдена")

        # Проверяем, что site_id равен 1
        if site_id != 1:
            raise Http404("Страница не найдена")

        return super().dispatch(request, *args, **kwargs)


"""Основные страницы"""

class ContactView(FormView):
    model = ContactPage
    template_name = 'contacts'
    form_class = ApplicationForm
    success_url = reverse_lazy('webmain:contact')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contacts'] = ContactPage.objects.first()
        try:
            seo_data = Seo.objects.get(pagetype=13)  # Фильтруем по домену
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

    def form_valid(self, form):
        form.instance.user = self.request.user if self.request.user.is_authenticated else None
        form.save()
        return super().form_valid(form)


"""Сотрудничества"""





"""Блог"""

class FaqsView(DomainTemplateMixin,ListView):
    model = Faqs
    template_name = 'faqs'  # No .html extension
    context_object_name = 'faqs'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_domain = self.request.get_host()
        try:
            seo_data = Seo.objects.get(pagetype=14, site__domain=current_domain)  # Фильтруем по домену
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

    def get_queryset(self):
        # Filter the queryset for the "blog" view based on the current domain
        current_domain = self.request.get_host()
        # Add your domain-specific logic here to filter Blogs queryset
        filtered_page = Faqs.objects.filter(site__domain=current_domain)
        return filtered_page

"""Блог"""
class BlogView(DomainTemplateMixin, ListView):
    model = Blogs
    template_name = 'blogs'
    context_object_name = 'blogs'
    paginate_by = 10

    def get_queryset(self):
        # Filter the queryset for the "blogs" view based on the current domain
        current_domain = self.request.get_host()
        print(current_domain)
        # Начинаем с базового QuerySet, отфильтрованного по домену
        blogs = Blogs.objects.filter(site__domain=current_domain).order_by('-create')
        # Получаем параметры из запроса
        category_id = self.request.GET.get('category', None)
        filter_type = self.request.GET.get('filter', None)
        search = self.request.GET.get('search', None)
        # Фильтруем по категории, если параметр присутствует
        if category_id:
            blogs = blogs.filter(category__id=category_id)

        if search:
            blogs = blogs.filter(name__icontains=search)
        # Применяем сортировку по типу фильтра
        if filter_type:
            if filter_type == "1":
                blogs = blogs.order_by('name')
            elif filter_type == "2":
                blogs = blogs.order_by('-create')
            elif filter_type == "3":
                blogs = blogs.order_by('create')
        return blogs  # Возвращаем отфильтрованный и отсортированный QuerySet

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Вызов `super()` сохраняет функциональность `ListView`
        current_domain = self.request.get_host()

        # Добавляем категории в контекст, фильтруя их по текущему домену
        context["categories"] = Categorys.objects.filter(site__domain=current_domain)

        try:
            seo_data = Seo.objects.get(pagetype=2, site__domain=current_domain)  # Фильтруем по домену
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

class BlogDetailView(DetailView):
    """Страницы"""
    model = Blogs
    template_name = 'webmain/blog_detail.html'
    context_object_name = 'blog'
    slug_field = "slug"

    def get_queryset(self):
        # Filter the queryset for the "blog" view based on the current domain
        current_domain = self.request.get_host()

        # Add your domain-specific logic here to filter Blogs queryset
        filtered_page = Blogs.objects.filter(site__domain=current_domain)

        return filtered_page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blogs = context['blog']
        current_domain = self.request.get_host()
        if blogs:
            context['pageinformation'] = blogs.description
            context['seo_previev'] = blogs.previev
            context['seo_title'] = blogs.title
            context['seo_description'] = blogs.content
            context['seo_propertytitle'] = blogs.propertytitle
            context['seo_propertydescription'] = blogs.propertydescription

            # Проверка и создание истории просмотра
            if self.request.user.is_authenticated:
                content_type = ContentType.objects.get_for_model(blogs)
                user = self.request.user

                # Проверяем, существует ли запись за сегодня
                today = now().date()
                history_exists = History.objects.filter(
                    user=user,
                    content_type=content_type,
                    object_id=blogs.id,
                    created_at__date=today
                ).exists()

                if not history_exists:
                    History.objects.create(
                        user=user,
                        content_type=content_type,
                        object_id=blogs.id
                    )
                    blogs.pageviews += 1
                    blogs.save()
        else:
            context['pageinformation'] = None
        return context

"""Сотрудничества"""

class PageDetailView(DomainTemplateMixin, DetailView):
    """Страницы"""
    model = Pages
    template_name = 'page_detail'
    context_object_name = 'page'
    slug_field = "slug"

    def get_queryset(self):
        # Filter the queryset for the "blog" view based on the current domain
        current_domain = self.request.get_host()

        # Add your domain-specific logic here to filter Blogs queryset
        filtered_page = Pages.objects.filter(site__domain=current_domain)

        return filtered_page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = context['page']
        if page:
            context['pageinformation'] = page.description
            context['seo_previev'] = page.previev
            context['seo_title'] = page.title
            context['seo_description'] = page.content
            context['seo_propertytitle'] = page.propertytitle
            context['seo_propertydescription'] = page.propertydescription
        else:
            context['pageinformation'] = None
        return context


"""Главная страница"""
class HomeView(DomainTemplateMixin, TemplateView):
    template_name = 'home'


"""Страница о нас"""
class AboutView(DomainTemplateMixin, TemplateView):
    template_name = 'about'


class SpecialistsView(DomainTemplateMixin, ListView):
    model = SettingsGlobale
    template_name = 'specialists'
    context_object_name = 'specialists'

    def get_queryset(self):
        # Filter the queryset for the "blogs" view based on the current domain
        current_domain = self.request.get_host()
        # Начинаем с базового QuerySet, отфильтрованного по домену
        filtered_page = SettingsGlobale.objects.filter(site__domain=current_domain)

        return filtered_page


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Вызов `super()` сохраняет функциональность `ListView`
        current_domain = self.request.get_host()

        try:
            seo_data = Seo.objects.get(pagetype=15, site__domain=current_domain)  # Фильтруем по домену
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


class DocumentationView(DomainTemplateMixin, ListView):
    model = DocumentationsSite
    template_name = 'documentation'
    context_object_name = 'documentation'

    def get_queryset(self):
        # Filter the queryset for the "blogs" view based on the current domain
        current_domain = self.request.get_host()
        # Начинаем с базового QuerySet, отфильтрованного по домену
        filtered_page = DocumentationsSite.objects.filter(site__domain=current_domain)

        return filtered_page


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Вызов `super()` сохраняет функциональность `ListView`
        current_domain = self.request.get_host()

        try:
            seo_data = Seo.objects.get(pagetype=16, site__domain=current_domain)  # Фильтруем по домену
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