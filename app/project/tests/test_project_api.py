"""Tests fot the project APIs."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Project,
    Tag,
    Milestone,
)

from project.serializers import (
    ProjectDetailSerializer,
)


PROJECTS_URL = reverse('project:project-list')


def detail_url(project_id):
    """Create and return a project detail URL."""

    return reverse('project:project-detail', args=[project_id])


def create_user(**params):
    """create and return a new user."""

    return get_user_model().objects.create_user(**params)


def create_project(user, **params):
    """ Create and return a sample project. """

    defaults = {
        'title': 'Sample project title',
        'time_hours': 22,
        'description': 'Sample description',
        'link': 'http://example.com/project.pdf',
    }
    defaults.update(params)

    project = Project.objects.create(user=user, **defaults)
    return project


class PublicProjectAPITests(TestCase):
    # Test unauthenticated API request.

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        # Test auth is required to call API.

        res = self.client.get(PROJECTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProjectApiTests(TestCase):
    # test authenticated Apri requests.

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')
        self.client.force_authenticate(self.user)

    def test_retrieve_projects(self):
        # Test retrieving a list of projects.

        create_project(user=self.user)
        create_project(user=self.user)

        res = self.client.get(PROJECTS_URL)

        projects = Project.objects.all().order_by('-id')
        serializer = ProjectDetailSerializer(projects, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_project_list_limited_to_user(self):
        """ Test list of projects is limited to authenticated user. """

        other_user = create_user(email='other@example.com', password='test123')
        create_project(user=other_user)
        create_project(user=self.user)

        res = self.client.get(PROJECTS_URL)

        projects = Project.objects.filter(user=self.user)
        serializer = ProjectDetailSerializer(projects, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_project_detail(self):
        """test get project detail. """

        project = create_project(user=self.user)

        url = detail_url(project.id)
        res = self.client.get(url)

        serializer = ProjectDetailSerializer(project)
        self.assertEqual(res.data, serializer.data)

    def test_create_project(self):
        """ Test creating a project. """

        payload = {
            'title': 'Sample project',
            'time_hours': 30,
        }
        res = self.client.post(PROJECTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        project = Project.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(project, k), v)
        self.assertEqual(project.user, self.user)

    def test_partial_update(self):
        """ test partial update of a project. """

        original_link = 'https://example.com/project.pdf'
        project = create_project(
            user=self.user,
            title='Sample project title',
            link=original_link,
        )

        payload = {'title': 'New project title'}
        url = detail_url(project.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        project.refresh_from_db()
        self.assertEqual(project.title, payload['title'])
        self.assertEqual(project.link, original_link)
        self.assertEqual(project.user, self.user)

    def test_full_update(self):
        """ test full update of project. """

        project = create_project(
            user=self.user,
            title='Sample project title',
            link='https://example.com/project.pdf',
            description='Sample project description',
        )

        payload = {
            'title': 'New project titile',
            'link': 'https://example.com/new-project.pdf',
            'description': 'New project description',
            'time_hours': 10,
        }
        url = detail_url(project.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        project.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(project, k), v)
        self.assertEqual(project.user, self.user)

    def test_update_user_return_error(self):
        """ Test changing the project user results in an error."""

        new_user = create_user(email='user2@example.com', password='test123')
        project = create_project(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(project.id)
        self.client.patch(url, payload)

        project.refresh_from_db()
        self.assertEqual(project.user, self.user)

    def test_delete_project(self):
        """Test deleting a project successful."""

        project = create_project(user=self.user)

        url = detail_url(project.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(id=project.id).exists())

    def test_delete_other_users_project_error(self):
        """Test trying to delete an other users project gives error."""

        new_user = create_user(email='user2@example.com', password='test123')
        project = create_project(user=new_user)

        url = detail_url(project.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Project.objects.filter(id=project.id).exists())

    def test_create_project_with_new_tags(self):
        """ Test creating a new project with new tags."""

        payload = {
            'title': 'Django Website',
            'time_hours': 30,
            'tags': [{'name': 'Django'}, {'name': 'Python'}],
        }
        res = self.client.post(PROJECTS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        projects = Project.objects.filter(user=self.user)
        self.assertEqual(projects.count(), 1)
        project = projects[0]
        self.assertEqual(project.tags.count(), 2)
        for tag in payload['tags']:
            exists = project.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_project_with_existing_tags(self):
        """Test creating a project with existing tags."""

        tag_improvment = Tag.objects.create(
            user=self.user,
            name='Self-Improvment'
        )
        payload = {
            'title': 'Self-improvment app',
            'time_hours': 60,
            'tags': [{'name': 'Self-Improvment'}, {'name': 'Django'}],
        }
        res = self.client.post(PROJECTS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        projects = Project.objects.filter(user=self.user)
        self.assertEqual(projects.count(), 1)
        project = projects[0]
        self.assertEqual(project.tags.count(), 2)
        self.assertIn(tag_improvment, project.tags.all())
        for tag in payload['tags']:
            exists = project.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Tets creatin tag when updationg a project."""

        project = create_project(user=self.user)

        payload = {'tags': [{'name': 'Python'}]}
        url = detail_url(project.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Python')
        self.assertIn(new_tag, project.tags.all())

    def test_update_project_assign_tag(self):
        """Test asigning an existing tag when updating a project"""

        tag_python = Tag.objects.create(user=self.user, name='Python')
        project = create_project(user=self.user)
        project.tags.add(tag_python)

        tag_django = Tag.objects.create(user=self.user, name='Djan')
        payload = {'tags': [{'name': 'Djan'}]}
        url = detail_url(project.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_django, project.tags.all())
        self.assertNotIn(tag_python, project.tags.all())

    def test_clear_project_tags(self):
        """Test Clearing a project tags."""

        tag = Tag.objects.create(user=self.user, name='JavaScript')
        project = create_project(user=self.user)
        project.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(project.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(project.tags.count(), 0)

    def test_create_project_with_new_milestones(self):
        """Test creating recipe with milestones"""

        payload = {
            'title': 'Test',
            'time_hours': 10,
            'milestones': [
                {
                    'title': 'FirstMilestone',
                    'hierarchycal_order': 1,
                    'order': 1,
                    'description': 'Sample description'
                },
                {
                    'title': 'FirstMilestoneSub',
                    'hierarchycal_order': 1,
                    'order': 2
                },
                {
                    'title': 'SecondMilestone',
                    'hierarchycal_order': 2,
                    'order': 1
                }
            ],
        }
        res = self.client.post(PROJECTS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        projects = Project.objects.filter(user=self.user)
        self.assertEqual(projects.count(), 1)
        project = projects[0]
        self.assertEqual(project.milestones.count(), 3)
        for milestone in payload['milestones']:
            exists = project.milestones.filter(
                title=milestone['title'],
                hierarchycal_order=milestone['hierarchycal_order'],
                order=milestone['order'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_milestone_add_on_update(self):
        """Tets creatin tag when updationg a project."""

        project = create_project(user=self.user)
        payload = {
            'milestones': [
                {
                    'title': 'FirstMilestone',
                    'hierarchycal_order': 1,
                    'order': 1,
                    'description': 'Sample description'
                },
                {
                    'title': 'FirstMilestoneSub',
                    'hierarchycal_order': 1,
                    'order': 2,
                    'description': 'Sample description'
                },
                {
                    'title': 'SecondMilestone',
                    'hierarchycal_order': 2,
                    'order': 1,
                    'description': 'Sample description'
                }
            ],
        }
        url = detail_url(project.id)

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_milestone = Milestone.objects.get(
            user=self.user,
            title='FirstMilestone'
        )
        self.assertIn(new_milestone, project.milestones.all())
        for milestone in payload['milestones']:
            exists = project.milestones.filter(
                title=milestone['title'],
                hierarchycal_order=milestone['hierarchycal_order'],
                order=milestone['order'],
                description=milestone['description'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)
