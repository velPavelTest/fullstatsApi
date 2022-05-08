from django.db import models
from users.models import CustomUser
from django.utils import timezone


class Subscription(models.Model):
    '''Подписка пользователей на артикулы для парсинга.'''
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    vendor_code = models.IntegerField(verbose_name='Артикул')
    # При подключении других магазинов/маркетплейсов может понадобиться замена артикула на строку.

    class Meta:
        unique_together = ['user', 'vendor_code']

    def __str__(self):
        return 'Артикул {0.vendor_code} для пользователя {0.user}'.format(self)


class ProductParseEntry(models.Model):
    vendor_code = models.IntegerField(verbose_name='Артикул')
    parse_time = models.DateTimeField(verbose_name='Дата парсинга', default=timezone.now)
    name = models.CharField(verbose_name='Наименование товара', max_length=255)
    price_wo_discount = models.DecimalField(verbose_name='Цена без скидки', max_digits=15, decimal_places=2)
    price_with_discount = models.DecimalField(verbose_name='Цена со скидкой', max_digits=15, decimal_places=2)
    brand = models.CharField(verbose_name='Бренд', max_length=255)
    seller = models.CharField(verbose_name='Поставщик', max_length=255)

    def __str__(self):
        return '{0.parse_time} {0.vendor_code} {0.price_with_discount} р'.format(self)
