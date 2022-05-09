from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser
from watch.models import Subscription, ProductParseEntry
import datetime
import pytz
from django.conf import settings


class ApiSubscribeTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_name = 'test_api_user'
        cls.password = 'hardPassword99'
        cls.user_name2 = 'test_api_user2'
        cls.password2 = 'hardPassword99'
        u1 = CustomUser.objects.create_user(cls.user_name, 'email@test.com', cls.password)
        u2 = CustomUser.objects.create_user(cls.user_name2, 'email2@test.com', cls.password2)
        cls.u1_id = u1.id
        cls.u2_id = u2.id
        for i in range(1, 11):
            Subscription.objects.create(user=u1, vendor_code=i)
        Subscription.objects.create(user=u2, vendor_code=2000)
        Subscription.objects.create(user=u2, vendor_code=2001)

    def get_access_token(self):
        url = '/api/token/'
        data = {'username': self.user_name, 'password': self.password}
        response = self.client.post(url, data, format='json')
        return response.data['access']

    def test_get_subsc_list(self):
        """Проверим возвращение списка подписок

        - API вернул 200.
        - Количество подписок в списке совпадает с количеством в БД
        - Нет чужой подписки
        - Все подписки совпали

        """
        url = '/watch/api/subscription/'
        access = self.get_access_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)
        response = client.get(url, data={'format': 'json'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sub_in_db = Subscription.objects.filter(user=self.u1_id).all()
        sub_in_resp = response.json()
        self.assertEqual(len(sub_in_db), len(sub_in_resp))
        v_code_db_set = set((a.vendor_code for a in sub_in_db))
        v_code_resp_set = set((a['vendor_code'] for a in sub_in_resp))
        self.assertEqual(v_code_db_set, v_code_resp_set)
        sub_u2 = Subscription.objects.filter(user=self.u2_id)[0]
        self.assertNotIn(sub_u2.vendor_code, v_code_db_set)  # Проверим, что в бд тоже нет такого артикула
        self.assertNotIn(sub_u2.vendor_code, v_code_resp_set)

    def test_add_subs(self):
        """Проверим добавление подписок

        - API вернул 201.
        - Подписка добавилась
        - Пользователь верный, артикул верный

        """
        url = '/watch/api/subscription/'
        access = self.get_access_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)
        response = client.post(url, {'vendor_code': 25}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        sub_in_db = Subscription.objects.filter(user=self.u1_id, vendor_code=25)
        self.assertEqual(1, len(sub_in_db))
        sub_in_db = sub_in_db[0]
        self.assertEqual(self.u1_id, sub_in_db.user.id)
        self.assertEqual(25, sub_in_db.vendor_code)

    def test_dell_subs(self):
        """Проверим удаление подписок

        - API вернул 301.
        - Подписка удалилась
        - Удалить чужую нельзя
        """
        url = '/watch/api/subscription/{}/'
        sub_in_db = Subscription.objects.filter(user=self.u1_id)[0]
        access = self.get_access_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)
        response = client.delete(url.format(sub_in_db.vendor_code), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        sub_in_db = Subscription.objects.filter(pk=sub_in_db.pk)
        self.assertEqual(0, len(sub_in_db))

        sub_in_db = Subscription.objects.filter(user=self.u2_id)[0]
        response = client.delete(url.format(sub_in_db.vendor_code), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        sub_in_db = Subscription.objects.filter(pk=sub_in_db.pk)
        self.assertEqual(1, len(sub_in_db))

    def test_no_post_access(self):
        url = '/watch/api/subscription/'
        client = APIClient()
        response = client.post(url, {'vendor_code': 26}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_list_access(self):
        url = '/watch/api/subscription/'
        client = APIClient()
        response = client.get(url, data={'format': 'json'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_del_access(self):
        url = '/watch/api/subscription/{}/'
        sub_in_db = Subscription.objects.filter(user=self.u1_id)[0]
        client = APIClient()
        response = client.delete(url.format(sub_in_db.vendor_code), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ApiReportTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_name = 'test_api_user'
        cls.password = 'hardPassword99'
        CustomUser.objects.create_user(cls.user_name, 'email@test.com', cls.password)
        cls.mass_vendor_code = 100
        cls.one_vendor_code = 10
        parse_date_naive = datetime.datetime(2022, 1, 9, 0, 0, 0)
        parse_date = pytz.timezone(settings.TIME_ZONE).localize(parse_date_naive, is_dst=None)
        delta = datetime.timedelta(hours=1)
        for _i in range(6*24):
            ProductParseEntry.objects.create(
                vendor_code=cls.mass_vendor_code,
                parse_time=parse_date,
                name='Name',
                price_wo_discount=100.00,
                price_with_discount=100.00,
                brand='Brand',
                seller='Seller',
            )
            parse_date += delta

        ProductParseEntry.objects.create(
            vendor_code=cls.mass_vendor_code,
            parse_time=pytz.timezone(settings.TIME_ZONE).localize(datetime.datetime(2022, 1, 11, 0, 30), is_dst=None),
            name='Name',
            price_wo_discount=110.00,
            price_with_discount=110.00,
            brand='Brand',
            seller='Seller',
        )
        ProductParseEntry.objects.create(
            vendor_code=cls.one_vendor_code,
            parse_time=pytz.timezone(settings.TIME_ZONE).localize(datetime.datetime(2022, 1, 12, 0, 30), is_dst=None),
            name='Name',
            price_wo_discount=110.00,
            price_with_discount=110.00,
            brand='Brand',
            seller='Seller',
        )

    def get_rep(self, v_code, start, end, period):
        url = '/api/token/'
        data = {'username': self.user_name, 'password': self.password}
        response = self.client.post(url, data, format='json')
        access = response.data['access']
        url = '/watch/api/report/{}/'.format(v_code)
        query = {'start': start, 'end': end, 'period': period}
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)
        response = client.get(url, data=query)
        return response

    def test_one_day(self):
        response = self.get_rep(self.mass_vendor_code, '2022-01-10', '2022-01-10', 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 24)

    def test_one_day_24h(self):
        response = self.get_rep(self.mass_vendor_code, '2022-01-10', '2022-01-10', 24)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_one_day_12h(self):
        response = self.get_rep(self.mass_vendor_code, '2022-01-10', '2022-01-10', 12)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_one_day_no_dublicates(self):
        response = self.get_rep(self.mass_vendor_code, '2022-01-11', '2022-01-11', 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 24)

    def test_one_day_no_other_product(self):
        response = self.get_rep(self.mass_vendor_code, '2022-01-12', '2022-01-12', 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 24)

    def test_four_days(self):
        response = self.get_rep(self.mass_vendor_code, '2022-01-10', '2022-01-13', 24)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 4)

    def test_no_acces(self):
        url = '/watch/api/report/{}/'.format(self.mass_vendor_code)
        query = {'start': '2022-01-10', 'end': '2022-01-10', 'period': 1}
        client = APIClient()
        response = client.get(url, params=query)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ApiSubscribeAlternativeTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_name = 'test_api_user'
        cls.password = 'hardPassword99'
        cls.user_name2 = 'test_api_user2'
        cls.password2 = 'hardPassword99'
        u1 = CustomUser.objects.create_user(cls.user_name, 'email@test.com', cls.password)
        u2 = CustomUser.objects.create_user(cls.user_name2, 'email2@test.com', cls.password2)
        cls.u1_id = u1.id
        cls.u2_id = u2.id
        for i in range(1, 11):
            Subscription.objects.create(user=u1, vendor_code=i)
        Subscription.objects.create(user=u2, vendor_code=2000)
        Subscription.objects.create(user=u2, vendor_code=2001)

    def get_access_token(self):
        url = '/api/token/'
        data = {'username': self.user_name, 'password': self.password}
        response = self.client.post(url, data, format='json')
        return response.data['access']

    def test_get_subsc_list(self):
        """Проверим возвращение списка подписок

        - API вернул 200.
        - Количество подписок в списке совпадает с количеством в БД
        - Нет чужой подписки
        - Все подписки совпали

        """
        url = '/watch/api/alternative/subscription/'
        access = self.get_access_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)
        response = client.get(url, data={'format': 'json'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sub_in_db = Subscription.objects.filter(user=self.u1_id).all()
        sub_in_resp = response.json()
        self.assertEqual(len(sub_in_db), len(sub_in_resp))
        v_code_db_set = set((a.vendor_code for a in sub_in_db))
        v_code_resp_set = set((a['vendor_code'] for a in sub_in_resp))
        self.assertEqual(v_code_db_set, v_code_resp_set)
        sub_u2 = Subscription.objects.filter(user=self.u2_id)[0]
        self.assertNotIn(sub_u2.vendor_code, v_code_db_set)  # Проверим, что в бд тоже нет такого артикула
        self.assertNotIn(sub_u2.vendor_code, v_code_resp_set)

    def test_add_subs(self):
        """Проверим добавление подписок

        - API вернул 201.
        - Подписка добавилась
        - Пользователь верный, артикул верный

        """
        url = '/watch/api/alternative/subscription/'
        access = self.get_access_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)
        response = client.post(url, {'vendor_code': 25}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        sub_in_db = Subscription.objects.filter(user=self.u1_id, vendor_code=25)
        self.assertEqual(1, len(sub_in_db))
        sub_in_db = sub_in_db[0]
        self.assertEqual(self.u1_id, sub_in_db.user.id)
        self.assertEqual(25, sub_in_db.vendor_code)

    def test_dell_subs(self):
        """Проверим удаление подписок

        - API вернул 301.
        - Подписка удалилась
        - Удалить чужую нельзя
        """
        url = '/watch/api/alternative/subscription/{}/'
        sub_in_db = Subscription.objects.filter(user=self.u1_id)[0]
        access = self.get_access_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)
        response = client.delete(url.format(sub_in_db.pk), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        sub_in_db = Subscription.objects.filter(pk=sub_in_db.pk)
        self.assertEqual(0, len(sub_in_db))

        sub_in_db = Subscription.objects.filter(user=self.u2_id)[0]
        response = client.delete(url.format(sub_in_db.pk), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        sub_in_db = Subscription.objects.filter(pk=sub_in_db.pk)
        self.assertEqual(1, len(sub_in_db))

    def test_no_post_access(self):
        url = '/watch/api/alternative/subscription/'
        client = APIClient()
        response = client.post(url, {'vendor_code': 26}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_list_access(self):
        url = '/watch/api/alternative/subscription/'
        client = APIClient()
        response = client.get(url, data={'format': 'json'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_del_access(self):
        url = '/watch/api/alternative/subscription/{}/'
        sub_in_db = Subscription.objects.filter(user=self.u1_id)[0]
        client = APIClient()
        response = client.delete(url.format(sub_in_db.pk), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
