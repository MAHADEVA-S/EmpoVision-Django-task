from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.generic import TemplateView
from rest_framework import permissions
from rest_framework.authtoken import views as token_views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(title="EmpoVision API", default_version="v1",
                 description="Employee, department, attendance and performance management API."),
    public=True, permission_classes=[permissions.AllowAny],
)
urlpatterns = [
    path("", TemplateView.as_view(template_name="dashboard.html"), name="dashboard"),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("api-token-auth/", token_views.obtain_auth_token, name="api-token-auth"),
    path("health/", lambda request: JsonResponse({"status": "ok"}), name="health"),
    path("swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
