from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "timezone", "email_notifications", "telegram_chat_id"]


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.none()

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Profile.objects.none()
        return Profile.objects.filter(user=self.request.user)
