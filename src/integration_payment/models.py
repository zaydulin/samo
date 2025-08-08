from random import randrange
from django.db import models
from django.conf import settings
from django.core.validators import (FileExtensionValidator)


# Create your models here.
class PaymentType(models.Model):
    """Страницы"""
    TYPE = [
        (1, 'Яндекс'),
        (2, 'Тинькоф'),
        (3, 'Gateway'),
        (4, 'АльфаБанк'),
    ]
    type = models.PositiveSmallIntegerField('Тип', choices=TYPE, blank=False, default=1)
    key_1 = models.TextField("Первый ключ (public key)")
    key_2 = models.CharField("Второй ключ (secret key)", max_length=550)
    shop_key = models.CharField("Ключ магазина (shop key)", max_length=550)
    content = models.TextField(blank=True, null=True, verbose_name='Описание')
    turn_on = models.BooleanField("Включить", default=False)
    image = models.FileField(upload_to='payment_type/%Y/%m/%d/', blank=True, null=True, verbose_name='Изображение', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)

    class Meta:
        verbose_name = "Способ оплаты"
        verbose_name_plural = "Способы оплаты"

"""Покупки"""
class Order(models.Model):
    STATUS = [
        (1, 'Оплата не прошла'),
        (2, 'Оплачено'),
    ]
    status = models.PositiveSmallIntegerField('Статус', choices=STATUS, blank=False, default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_DEFAULT, blank=True, null=True, verbose_name="Пользователь", default=None)
    created_timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания заказа")
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефона")
    customer_name = models.CharField(max_length=200, verbose_name="Имя")
    customer_surname = models.CharField(max_length=200, verbose_name="Фамилия")
    customer_email = models.CharField(max_length=200, verbose_name="Адрес эл почты")
    amount = models.PositiveSmallIntegerField(default=0, verbose_name='Сумма')
    key = models.CharField(verbose_name="Ключ", max_length=32, unique=True, blank=True)
    purchase_url = models.TextField(verbose_name="Покупка юрл", blank=True, null=True)

    def save(self, *args, **kwargs):
        loop_num = 0
        unique = False
        while not self.key and not unique:
            if loop_num < settings.RANDOM_URL_MAX_TRIES:
                new_key = ''
                for i in range(settings.RANDOM_URL_LENGTH):
                    new_key += settings.RANDOM_URL_CHARSET[
                        randrange(0, len(settings.RANDOM_URL_CHARSET))]
                if not Order.objects.filter(key=new_key):
                    self.key = new_key
                    unique = True
                loop_num += 1
            else:
                raise ValueError("Couldn't generate a unique code.")

        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return f"Заказ № {self.pk} | Покупатель {self.customer_name} {self.customer_surname}"

    class Meta:
        db_table = "order"
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

