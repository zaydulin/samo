# Ваш файл middlewares.py

from django.utils import timezone
from .models import Profile  # Импортируйте вашу модель Profile

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            # Обновляем статус пользователя
            Profile.objects.filter(id=request.user.id).update(online=True)
        return response
