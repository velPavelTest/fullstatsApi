from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser
from watch.models import Subscription


class ApiTest(APITestCase):

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
        response = client.delete(url.format(sub_in_db.pk), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        sub_in_db = Subscription.objects.filter(pk=sub_in_db.pk)
        self.assertEqual(0, len(sub_in_db))

        sub_in_db = Subscription.objects.filter(user=self.u2_id)[0]
        response = client.delete(url.format(sub_in_db.pk), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        sub_in_db = Subscription.objects.filter(pk=sub_in_db.pk)
        self.assertEqual(1, len(sub_in_db))
