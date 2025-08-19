from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.db.models import Count
from functools import wraps
from .forms import RegisterForm
from .models import User

def admin_required(view_func):
    """
    装饰器：只允许特定管理员邮箱访问
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.email != '564999607@qq.com':
            return HttpResponseForbidden("访问被拒绝：您没有权限访问此页面")
        return view_func(request, *args, **kwargs)
    return wrapper

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})

@admin_required
def user_list(request):
    """
    用户管理页面 - 只有特定管理员可以访问
    显示所有用户的详细统计信息
    """
    # 获取用户及其相关统计数据
    users = User.objects.select_related().prefetch_related(
        'workentry_set', 'report_set'
    ).annotate(
        work_count=Count('workentry_set', distinct=True),
        report_count=Count('report_set', distinct=True)
    ).order_by("-date_joined")
    
    # 为每个用户添加额外信息
    user_data = []
    for user in users:
        user_data.append({
            'user': user,
            'username': user.email.split('@')[0],  # 从邮箱提取用户名
            'work_count': user.work_count,
            'report_count': user.report_count,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
        })
    
    return render(request, "accounts/user_list.html", {
        "user_data": user_data,
        "total_users": len(user_data)
    })
