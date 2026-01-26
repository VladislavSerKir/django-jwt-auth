from rest_framework import serializers
from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = Note
        fields = ('id', 'name', 'description', 'user',
                  'user_name', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
