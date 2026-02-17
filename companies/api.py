from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsOwner

from .models import Company, Contact


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "website", "notes", "created_at", "updated_at"]


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            "id",
            "company",
            "name",
            "email",
            "phone",
            "title",
            "notes",
            "created_at",
            "updated_at",
        ]


class OwnerScopedModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CompanyViewSet(OwnerScopedModelViewSet):
    serializer_class = CompanySerializer
    search_fields = ["name", "notes", "website"]
    ordering_fields = ["name", "created_at", "updated_at"]
    queryset = Company.objects.none()

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Company.objects.none()
        return Company.objects.filter(owner=self.request.user)


class ContactViewSet(OwnerScopedModelViewSet):
    serializer_class = ContactSerializer
    filterset_fields = ["company"]
    search_fields = ["name", "email", "phone", "title"]
    ordering_fields = ["name", "created_at", "updated_at"]
    queryset = Contact.objects.none()

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Contact.objects.none()
        return Contact.objects.filter(owner=self.request.user).select_related("company")
