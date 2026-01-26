from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet, AdminNoteViewSet

router = DefaultRouter()
router.register(r'', NoteViewSet, basename='note')
router.register(r'admin/all', AdminNoteViewSet, basename='admin-note')

urlpatterns = [
    path('', include(router.urls)),
]
