from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.http import JsonResponse
from django.views.decorators.cache import never_cache

@never_cache
def health_check(request):
    """健康检查端点"""
    return JsonResponse({
        'status': 'ok',
        'message': 'WorkReport is running'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('', include('apps.worklog.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('reports/', include('apps.reports.urls')),
    path('', RedirectView.as_view(url='/dashboard/')),
]
