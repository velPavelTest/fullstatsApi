from django.test import TestCase
from django.test import Client
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from users.models import CustomUser


class RegisterTest(TestCase):
    def test_success_register(self):
        c = Client()
        data = {'username': 'registered_user', 'email': 'reg@email.com',
                'password1': 'hardPassword99', 'password2': 'hardPassword99'}
        response = c.post('/register/', data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        u = CustomUser.objects.get(username=data['username'])
        self.assertEqual(u.email, u.email)


class JwtTokenTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_name = 'test_api_user'
        cls.password = 'hardPassword99'
        CustomUser.objects.create_user(cls.user_name, 'email@test.com', cls.password)

    def get_tokens(self):
        url = '/api/token/'
        data = {'username': self.user_name, 'password': self.password}
        response = self.client.post(url, data, format='json')
        return response.data

    def test_get_access_refresh_valid(self):
        """
        Можем получить access и refresh токены
        """
        url = '/api/token/'
        data = {'username': self.user_name, 'password': self.password}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_get_access_refresh_invalid(self):
        """
        По неверному паролю токены не дадут
        """
        url = '/api/token/'
        data = {'username': self.user_name, 'password': 'b'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('refresh', response.data)
        self.assertNotIn('access', response.data)

    def test_refresh_valid(self):
        url = '/api/token/refresh/'
        refresh = self.get_tokens()['refresh']
        data = {'refresh': refresh}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_refresh_invalid(self):
        url = '/api/token/refresh/'
        data = {'refresh': 'aaaa'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('refresh', response.data)
        self.assertNotIn('access', response.data)

    def test_jwt_authorisation_valid(self):
        url = '/api/token/testaccess/'
        access = self.get_tokens()['access']
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)
        response = client.get(url, data={'format': 'json'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'Ok'})
        self.assertNotIn('access', response.data)

    def test_jwt_authorisation_invalid(self):
        url = '/api/token/testaccess/'
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'abc')
        response = client.get(url, data={'format': 'json'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_authorisation_without(self):
        url = '/api/token/testaccess/'
        client = APIClient()
        response = client.get(url, data={'format': 'json'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
