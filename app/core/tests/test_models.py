from django.test import TestCase
from django.contrib.auth import get_user_model


class testUserModel(TestCase):

    def test_create_user_success(self):
        """Test that normal user is created"""
        email = 'test@gmail.com'
        password = 'testpassword123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_superuser_success(self):
        """Test that super user is created"""
        email = 'test@gmail.com'
        password = 'testpassword123'
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_serialized(self):
        """Test that the new user email is normalize (lowercase afer @)"""
        email = 'test@gmaIl.coM'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'testpassword123')
