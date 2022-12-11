"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='user@example.com', password='123password'):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_project(self):
        """Test creating a project is succesfull."""

        user = get_user_model().objects.create_user(
            'test@example.com'
            'testpass123'
        )
        project = models.Project.objects.create(
            user=user,
            title='Sample project name',
            time_hours=50,
            description='Sample project description',
        )

        self.assertEqual(str(project), project.title)

    def test_create_tag(self):
        """Test creating a tag is successful."""

        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_project_secions(self):
        """Test creating a project section is successful."""

        user = create_user()
        project = models.Project.objects.create(
            user=user,
            title='Sample project name',
            time_hours=50,
            description='Sample project description',
        )
        project_section = models.Milestone.objects.create(
            user=user, title='Test',
            hierarchycal_order=1,
            order=1,
            project=project
        )

        self.assertEqual(1, project_section.hierarchycal_order)
        self.assertEqual(1, project_section.order)
        self.assertEqual(project, project_section.project)
