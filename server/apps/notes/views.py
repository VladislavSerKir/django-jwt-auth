from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from apps.users.enums import Role
from apps.users.middleware import method_roles
from .models import Note
from .serializers import NoteSerializer


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'name']

    def get_queryset(self):
        user = self.request.user

        return Note.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@method_roles(Role.ADMIN)
class AdminNoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'name']
