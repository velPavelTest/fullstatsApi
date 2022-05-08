from celery import shared_task
# from requests import HTTPError
from .models import Subscription, ProductParseEntry
from .services import get_wildberries_parsed_product
from django.utils import timezone
import datetime


@shared_task()
def find_vendor_codes_to_parse():
    """Выборка всез активных артикулов и запуск по ним парсинга"""
    for s in Subscription.objects.values('vendor_code').distinct():
        parce_product.apply_async((s['vendor_code'],), expires=timezone.now()+datetime.timedelta(minutes=59))


# @shared_task(bind=True, autoretry_for=(HTTPError,), retry_kwargs={'max_retries': 2, 'countdown': 300})
# пока autoretry_for конфликтует с expires баг https://github.com/celery/celery/issues/7091
# @task поискать и воткнуть обходной вызов retry
@shared_task(bind=True)
def parce_product(self, vendor_id: int):
    """Парсинг данных с карточки продукта"""
    parsed: ProductParseEntry = get_wildberries_parsed_product(vendor_id)
    if parsed is not None:
        parsed.save()
