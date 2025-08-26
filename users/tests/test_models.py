# users/tests/test_models.py

from django.test import TestCase
from .models import CustomUser

class UserModelTest(TestCase):

    def test_user_creation(self):
        """
        Tests that a CustomUser can be created with a specific role.
        """
        user = CustomUser.objects.create_user(
            username='testagent',
            email='agent@test.com',
            password='password123',
            role='agent'
        )
        self.assertEqual(user.username, 'testagent')
        self.assertEqual(user.role, 'agent')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)