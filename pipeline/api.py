from rest_framework import serializers

from .models import ApplicationEvent


class ApplicationEventSerializer(serializers.ModelSerializer):
    application = serializers.PrimaryKeyRelatedField(read_only=True)
    type = serializers.CharField(source="event_type.code", read_only=True)
    event_type_code = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = ApplicationEvent
        fields = [
            "id",
            "application",
            "type",
            "event_type",
            "event_type_code",
            "scheduled_at",
            "completed_at",
            "outcome",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["event_type"]

    def create(self, validated_data):
        from .models import EventType

        event_type_code = validated_data.pop("event_type_code")
        event_type, _ = EventType.objects.get_or_create(
            code=event_type_code,
            defaults={"label": event_type_code.replace("_", " ").title()},
        )
        validated_data["event_type"] = event_type
        return super().create(validated_data)

    def update(self, instance, validated_data):
        from .models import EventType

        event_type_code = validated_data.pop("event_type_code", None)
        if event_type_code:
            event_type, _ = EventType.objects.get_or_create(
                code=event_type_code,
                defaults={"label": event_type_code.replace("_", " ").title()},
            )
            validated_data["event_type"] = event_type
        return super().update(instance, validated_data)
