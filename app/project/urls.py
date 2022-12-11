"""
URL mappings for the project app.
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from project import views


router = DefaultRouter()
router.register('projects', views.ProjectViewSet)
router.register('tags', views.TagViewSet)

app_name = 'project'

urlpatterns = [
    path('', include(router.urls)),
]
