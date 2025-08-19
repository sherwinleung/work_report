from django.urls import path
from . import views

urlpatterns = [
    path("generate/", views.report_generate, name="report_generate"),
    path("<int:pk>/", views.report_detail, name="report_detail"),
    path("", views.report_list, name="report_list"),
]
