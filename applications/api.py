from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsOwner

from .models import JobApplication, StatusHistory, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class JobApplicationSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=False)

    class Meta:
        model = JobApplication
        fields = [
            "id",
            "company",
            "primary_contact",
            "role_title",
            "source",
            "job_url",
            "location_type",
            "location_text",
            "salary_min",
            "salary_max",
            "currency",
            "applied_date",
            "status",
            "priority",
            "notes",
            "next_action_at",
            "next_action_text",
            "tags",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        salary_min = attrs.get("salary_min")
        salary_max = attrs.get("salary_max")
        if salary_min is not None and salary_max is not None and salary_min > salary_max:
            raise serializers.ValidationError("salary_min must be less than or equal salary_max")
        return attrs

    def validate_tags(self, tags):
        owner = self.context["request"].user
        invalid = [tag.id for tag in tags if tag.owner_id != owner.id]
        if invalid:
            raise serializers.ValidationError("Tags must belong to the authenticated owner")
        return tags

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        obj = super().create(validated_data)
        if tags:
            obj.tags.set(
                Tag.objects.filter(owner=self.context["request"].user, pk__in=[t.pk for t in tags])
            )
        return obj

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        obj = super().update(instance, validated_data)
        if tags is not None:
            obj.tags.set(
                Tag.objects.filter(owner=self.context["request"].user, pk__in=[t.pk for t in tags])
            )
        return obj


class StatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusHistory
        fields = [
            "id",
            "application",
            "from_status",
            "to_status",
            "changed_at",
            "changed_by",
            "note",
        ]


class OwnerScopedModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class JobApplicationViewSet(OwnerScopedModelViewSet):
    serializer_class = JobApplicationSerializer
    filterset_fields = ["status", "source", "location_type", "priority", "company"]
    search_fields = ["role_title", "company__name", "notes"]
    ordering_fields = ["applied_date", "next_action_at", "priority", "created_at", "updated_at"]
    queryset = JobApplication.objects.none()

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return JobApplication.objects.none()
        return (
            JobApplication.objects.filter(owner=self.request.user)
            .select_related("company", "primary_contact")
            .prefetch_related("tags")
        )


class TagViewSet(OwnerScopedModelViewSet):
    serializer_class = TagSerializer
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
    queryset = Tag.objects.none()

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Tag.objects.none()
        return Tag.objects.filter(owner=self.request.user)
