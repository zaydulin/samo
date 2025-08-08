from importlib import import_module
from django.conf import settings
from django.urls import include, path, clear_url_caches, resolve, Resolver404, reverse
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
import redis

# Сопоставляем домены с URL-конфигурациями и пространствами имен
DOMAIN_URLS = {
    "mentro.ru": ("webmain.urls", "webmain"),
    "ms.mentro.ru": ("moderation.urls", "moderation"),
    "lk.mentro.ru": ("useraccount.urls", "useraccount"),
}


NAMESPACE_TO_DOMAIN = {
    "webmain": "mentro.ru",
    "moderation": "ms.mentro.ru",
    "useraccount": "lk.mentro.ru",
}

from django.core.cache import cache

class DomainURLsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith(settings.STATIC_URL) or request.path.startswith(settings.MEDIA_URL):
            return None

        host = request.get_host().split(':')[0]

        # Логика доменов (остается без изменений)
        url_config = DOMAIN_URLS.get(host)
        if not url_config:
            return self.get_response(request)

        urls_module_path, namespace = url_config
        try:
            root_urlconf = import_module(settings.ROOT_URLCONF)
            site_urls = import_module(urls_module_path)
            root_urlconf.urlpatterns = [path('', include((site_urls, namespace)))] + root_urlconf.urlpatterns
            request.urlconf = root_urlconf
            clear_url_caches()
        except ImportError:
            raise ImproperlyConfigured(f"URL конфигурация для поддомена {host} не найдена.")

        current_path = request.path_info
        try:
            resolved_url = resolve(current_path, urlconf=request.urlconf)
            resolved_namespace = resolved_url.namespace
            expected_host = NAMESPACE_TO_DOMAIN.get(resolved_namespace)
            is_ajax_request = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

            if not is_ajax_request and expected_host and expected_host != host:
                new_url = request.build_absolute_uri().replace(host, expected_host)
                return HttpResponseRedirect(new_url)
        except Resolver404:
            pass

        return None

    def process_response(self, request, response):
        response["Access-Control-Allow-Origin"] = "https://mentro.ru"
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Origin, Content-Type, Accept, Authorization, X-Requested-With"

        if request.path == reverse('set_language'):
            language = request.POST.get('language', settings.LANGUAGE_CODE)
            translation.activate(language)
            response.set_cookie('django_language', language, domain=".mentro.ru")  # Изменено для всех поддоменов
        return response