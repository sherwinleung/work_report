from django.urls import path
from . import views

urlpatterns = [
    path("generate/", views.report_generate, name="report_generate"),
    path("api-management/", views.api_management, name="api_management"),
    path("test-api/", views.test_api_connection, name="test_api_connection"),
    path("<int:pk>/", views.report_detail, name="report_detail"),
    path("", views.report_list, name="report_list"),
]
