from django.urls import path
from . import views

urlpatterns = [
    path("", views.redirect_dashboard, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("work/", views.work_list_create, name="work_list_create"),
    path("work/<int:pk>/delete/", views.work_delete, name="work_delete"),
]
