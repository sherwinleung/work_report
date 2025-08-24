from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.core.paginator import Paginator
from datetime import date, timedelta
import json
from .models import WorkEntry

def redirect_dashboard(request):
    return redirect("dashboard")

@login_required
def dashboard(request):
    # 处理按日统计的日期范围
    start = request.GET.get("start")
    end = request.GET.get("end")
    if start and end:
        try:
            start_date = date.fromisoformat(start)
            end_date = date.fromisoformat(end)
        except Exception:
            start_date = date.today() - timedelta(days=6)
            end_date = date.today()
    else:
        start_date = date.today() - timedelta(days=6)
        end_date = date.today()
    
    # 处理图表的日期范围（独立于按日统计）
    chart_start = request.GET.get("chart_start")
    chart_end = request.GET.get("chart_end")
    
    if chart_start and chart_end:
        try:
            chart_start_date = date.fromisoformat(chart_start)
            chart_end_date = date.fromisoformat(chart_end)
        except Exception:
            chart_start_date = None
            chart_end_date = None
    else:
        chart_start_date = None
        chart_end_date = None
    
    # 如果没有指定图表日期范围，使用默认的最近1个月
    if not chart_start_date or not chart_end_date:
        # 获取用户的第一条工作记录日期
        first_entry = WorkEntry.objects.filter(user=request.user).order_by('date').first()
        
        if first_entry:
            # 如果有数据，默认显示最近1个月，但不早于第一条记录
            chart_end_date = date.today()
            chart_start_date = max(
                chart_end_date - timedelta(days=30),  # 最近1个月
                first_entry.date  # 不早于第一条记录
            )
        else:
            # 如果没有数据，显示最近7天
            chart_start_date = date.today() - timedelta(days=6)
            chart_end_date = date.today()

    # 按日统计的数据（用于左侧表格）
    qs = WorkEntry.objects.filter(user=request.user, date__range=(start_date, end_date))
    agg = qs.aggregate(total_minutes=Sum("duration_minutes"), records=Count("id"))
    total_minutes = agg.get("total_minutes") or 0
    total_hours = round(total_minutes / 60.0, 2)

    by_day = (qs.values("date")
                .annotate(total_minutes=Sum("duration_minutes"), records=Count("id"))
                .order_by("date"))
    by_day_list = []
    for r in by_day:
        r = dict(r)
        r["total_hours"] = round((r.get("total_minutes") or 0) / 60.0, 2)
        by_day_list.append(r)
    
    # 图表数据（使用独立的日期范围）
    chart_qs = WorkEntry.objects.filter(user=request.user, date__range=(chart_start_date, chart_end_date))
    chart_by_day = (chart_qs.values("date")
                    .annotate(total_minutes=Sum("duration_minutes"), records=Count("id"))
                    .order_by("date"))
    
    chart_labels = []
    chart_hours = []
    chart_records = []
    chart_dates = []
    
    for r in chart_by_day:
        r = dict(r)
        chart_hours_val = round((r.get("total_minutes") or 0) / 60.0, 2)
        
        # 为图表准备数据
        chart_labels.append(r["date"].strftime("%m-%d"))
        chart_hours.append(chart_hours_val)
        chart_records.append(r["records"])
        chart_dates.append(r["date"].isoformat())
    
    # 为图表准备JSON数据
    chart_data = {
        "labels": chart_labels,
        "hours": chart_hours,
        "records": chart_records,
        "dates": chart_dates
    }

    return render(request, "worklog/dashboard.html", {
        "start_date": start_date, "end_date": end_date,
        "agg": agg, "total_hours": total_hours, "by_day": by_day_list,
        "chart_data": json.dumps(chart_data),
        "chart_start_date": chart_start_date,
        "chart_end_date": chart_end_date,
    })

@login_required
def work_list_create(request):
    if request.method == "POST":
        start_time_str = request.POST.get("start_time")
        end_time_str = request.POST.get("end_time")
        
        date_str = request.POST.get("date")
        title = request.POST.get("title","")
        content = request.POST.get("content","")
        start_time = request.POST.get("start_time") or None
        end_time = request.POST.get("end_time") or None
        if date_str and content:
            from datetime import date as _d, time as _t
            d = _d.fromisoformat(date_str)
            st = _t.fromisoformat(start_time) if start_time else None
            et = _t.fromisoformat(end_time) if end_time else None
            WorkEntry.objects.create(user=request.user, date=d, start_time=st, end_time=et, title=title, content=content)
        return redirect("work_list_create")

    # 获取分页参数
    page = request.GET.get('page', 1)
    
    items_qs = WorkEntry.objects.filter(user=request.user).order_by("-date","-created_at")
    
    # 准备数据
    items_list = []
    for it in items_qs:
        hours = round((it.duration_minutes or 0) / 60.0, 2)
        items_list.append({"obj": it, "hours": hours})
    
    # 分页处理，每页显示10条记录
    paginator = Paginator(items_list, 10)
    items = paginator.get_page(page)
    
    return render(request, "worklog/work_list.html", {
        "items": items,
        "today_date": date.today().isoformat(),  # 添加今天的日期
    })

@login_required
def work_delete(request, pk):
    item = get_object_or_404(WorkEntry, pk=pk, user=request.user)
    item.delete()
    
    # 获取当前页面参数，删除后回到同一页
    page = request.GET.get('page', 1)
    return redirect(f"{request.path.replace(f'/{pk}/delete/', '')}?page={page}")
