from django.test import TestCase
from django.contrib.auth import get_user_model

class testUserModel(TestCase):

    def test_create_user_success(self):
        email = 'test@gmail.com'
        password = 'testpassword123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email )
        self.assertTrue(user.check_password(password))

    def test_create_superuser_success(self):
        email = 'test@gmail.com'
        password = 'testpassword123'
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_serialized(self):
        """Test that the new user email is normalize"""
        email = 'test@gmaIl.coM'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())