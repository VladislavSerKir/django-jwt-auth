# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Notes API",
        default_version='v1',
        description="API for notes management with JWT authentication",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


def home_view(request):
    return HttpResponse("""
    <h1>Django JWT Auth API</h1>
    <p>Welcome to the API!</p>
    <ul>
        <li><a href="/admin/">Admin Panel</a></li>
        <li><a href="/swagger/">API Documentation (Swagger)</a></li>
        <li><a href="/redoc/">API Documentation (ReDoc)</a></li>
        <li><a href="/api/auth/register/">Register</a></li>
        <li><a href="/api/auth/login/">Login</a></li>
    </ul>
    """)


urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/notes/', include('apps.notes.urls')),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
]
