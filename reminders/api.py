from rest_framework import serializers

from .models import Reminder


class ReminderSerializer(serializers.ModelSerializer):
    application = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Reminder
        fields = [
            "id",
            "application",
            "remind_at",
            "channel",
            "message",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status"]
