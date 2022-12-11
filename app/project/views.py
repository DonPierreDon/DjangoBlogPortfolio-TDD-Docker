"""
Views for the project APIs.
"""
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Project,
    Tag,
)
from project import serializers


class ProjectViewSet(viewsets.ModelViewSet):
    """View for manage Project APIs."""
    serializer_class = serializers.ProjectDetailSerializer
    queryset = Project.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Retrieve projects for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serialize_class(self):
        """Return the serializer class for requests."""
        if self.action == 'list':
            return serializers.ProjectSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new project."""
        serializer.save(user=self.request.user)


class TagViewSet(mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to autheticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')
