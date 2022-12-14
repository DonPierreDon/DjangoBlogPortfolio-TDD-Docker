"""
Serialaziers for project APIs
"""
from rest_framework import serializers

from core.models import (
    Project,
    Tag,
    Milestone
)

from rest_flex_fields import FlexFieldsModelSerializer


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class MilestoneSerializer(FlexFieldsModelSerializer):
    """Serializer for milestones of projects"""

    class Meta:
        model = Milestone
        fields = ['title', 'hierarchycal_order', 'order', 'description']
        read_only_fields = ['id']


class ProjectSerializer(FlexFieldsModelSerializer):
    """Serializer for projects"""
    tags = TagSerializer(many=True, required=False)
    milestones = MilestoneSerializer(
        many=True,
        required=False,
        fields=['title', 'hierarchycal_order', 'order']
    )

    class Meta:
        model = Project
        fields = ['id', 'title', 'time_hours', 'link', 'tags', 'milestones']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, project):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            project.tags.add(tag_obj)

    def _create_milestones(self, milestones, project):
        """Handle creating milestones as needed."""
        auth_user = self.context['request'].user
        for milestone in milestones:
            milestone_obj = Milestone.objects.create(
                user=auth_user,
                project=project,
                **milestone,
            )
            project.milestones.add(milestone_obj)

    def create(self, validated_data):
        """Create a project."""
        milestones = validated_data.pop('milestones', [])
        tags = validated_data.pop('tags', [])
        project = Project.objects.create(**validated_data)
        self._get_or_create_tags(tags, project)
        self._create_milestones(milestones, project)

        return project

    def update(self, instance, validated_data):
        """Update Project"""
        tags = validated_data.pop('tags', None)
        milestones = validated_data.pop('milestones', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if milestones is not None:
            instance.milestones.clear()
            self._create_milestones(milestones, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ProjectDetailSerializer(ProjectSerializer):
    """Serializer for project detail view."""
    milestones = MilestoneSerializer(
        many=True,
        required=False,
        fields=['title', 'hierarchycal_order', 'order', 'description']
    )

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['description']
