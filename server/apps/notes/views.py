from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Note
from .serializers import NoteSerializer


class NoteViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        notes = Note.objects.filter(user=request.user)
        serializer = NoteSerializer(notes, many=True)
        return Response({'notes': serializer.data})

    def create(self, request):
        serializer = NoteSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'note': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        note = get_object_or_404(Note, id=pk)

        if note.user != request.user:
            return Response(
                {'error': 'You do not have permission to access this note'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = NoteSerializer(note)
        return Response({'note': serializer.data})

    def update(self, request, pk=None):
        note = get_object_or_404(Note, id=pk)

        if note.user != request.user:
            return Response(
                {'error': 'You do not have permission to update this note'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = NoteSerializer(note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'note': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        note = get_object_or_404(Note, id=pk)

        if note.user != request.user:
            return Response(
                {'error': 'You do not have permission to delete this note'},
                status=status.HTTP_403_FORBIDDEN
            )

        note_id = note.id
        note.delete()
        return Response({'id': note_id}, status=status.HTTP_200_OK)
