from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from search.models import SearchRequest

User = get_user_model()

class APITests(APITestCase):
    def setUp(self):
        # Criando usuários sem 'username' conforme seu CustomUser
        self.user1 = User.objects.create_user(email='user1@test.com', password='password123')
        self.user2 = User.objects.create_user(email='user2@test.com', password='password123')
        
        self.search_req = SearchRequest.objects.create(
            user=self.user1,
            keywords='Engenharia de Software',
            notification_email='user1@test.com'
        )

    def test_authenticated_ownership(self):
        """Valida que o usuário só vê os próprios dados."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/v1/search-requests/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        self.client.force_authenticate(user=self.user2)
        response = self.client.get('/api/v1/search-requests/')
        self.assertEqual(len(response.data['results']), 0)