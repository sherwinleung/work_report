from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.worklog.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('reports/', include('apps.reports.urls')),
    path('', RedirectView.as_view(url='/dashboard/')),
]
