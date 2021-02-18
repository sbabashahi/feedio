from django.db import transaction
from rest_framework import serializers

from authnz.models import User


class RegisterLoginEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=5, max_length=50)
    password = serializers.CharField(min_length=5, max_length=50)


class MyProfileSerializer(serializers.Serializer):
    email = serializers.ReadOnlyField()
    email_confirmed = serializers.ReadOnlyField()
    first_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=50, required=False, allow_blank=True)

    @transaction.atomic
    def update(self, instance, validated_data):
        instance = User.objects.select_for_update().get(id=instance.id)
        if validated_data.get('first_name') and instance.first_name != validated_data['first_name']:
            instance.first_name = validated_data['first_name']
        elif validated_data.get('first_name', None) is not None:  # blank
            instance.first_name = ''

        if validated_data.get('last_name') and instance.last_name != validated_data['last_name']:
            instance.last_name = validated_data['last_name']
        elif validated_data.get('last_name', None) is not None:  # blank
            instance.last_name = ''

        instance.save(update_fields=['first_name', 'last_name'])
        return instance


class NestedUserSerializer(serializers.Serializer):
    username = serializers.ReadOnlyField()
