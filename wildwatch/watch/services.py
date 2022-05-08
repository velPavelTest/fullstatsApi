import requests
from bs4 import BeautifulSoup
from .models import ProductParseEntry
from decimal import Decimal, getcontext
from django.utils import timezone


def get_page(url: str) -> requests.models.Response:
    headers = {
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r


def get_wildberries_parsed_product(vendor_code: int) -> ProductParseEntry:
    """Парсинг информации из карточки товара wildberries. Возвращаем экземпляр модели или None

    Exceptions:
        HTTPError -
        Ошибки обращения к None object - на странице нет нужной информации.
    """

    url_product = 'https://www.wildberries.ru/catalog/{}/detail.aspx'.format(vendor_code)

    r = get_page(url_product)
    soup = BeautifulSoup(r.text, 'html.parser')

    brand: str = soup.find('span', attrs={'data-link': 'text{:product^brandName}'}).get_text(strip=True)
    name: str = soup.find('span', attrs={'data-link': 'text{:product^goodsName}'}).get_text(strip=True)

    getcontext().prec = 2
    price_str = soup.find('span', class_='price-block__final-price')
    if price_str is None:
        # @add_log
        # @question_ba возможно в случае отсутствия цены стоит сохранять эту инфу в БД.
        # Например, введя поле наличия товара. Использование Null спорно в цене спорно.
        # print('Нет цены')
        return None
    price: Decimal = Decimal(price_str.get_text(strip=True).replace('\xa0', '').replace('₽', ''))

    old_price_str = soup.find(class_='price-block__old-price j-final-saving')
    if old_price_str is not None:
        # если нет скидки, то обе цены равны
        old_price: Decimal = Decimal(old_price_str.get_text(strip=True).replace('\xa0', '').replace('₽', ''))
    else:
        old_price: Decimal = price

    # Данные о продавце грузятся js. Грузить Selenium не хочется, так что будем дёргать их json
    url_seller: str = 'https://wbx-content-v2.wbstatic.net/sellers/{}.json'.format(vendor_code)
    r = get_page(url_seller)
    # Доступны два названия продавца. Отображаемая на странице товара(тм) ["trademark"]
    # и юр. наименование ['supplierName']. Отображается на странице в деталях.
    # Судя по ТЗ нам нужно второе
    seller: str = r.json()['supplierName']

    return ProductParseEntry(vendor_code=vendor_code, name=name, brand=brand,
                             price_wo_discount=old_price,  price_with_discount=price,
                             seller=seller, parse_time=timezone.now())
