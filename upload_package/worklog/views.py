from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from datetime import date, timedelta
from .models import WorkEntry

def redirect_dashboard(request):
    return redirect("dashboard")

@login_required
def dashboard(request):
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

    return render(request, "worklog/dashboard.html", {
        "start_date": start_date, "end_date": end_date,
        "agg": agg, "total_hours": total_hours, "by_day": by_day_list
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

    items_qs = WorkEntry.objects.filter(user=request.user).order_by("-date","-created_at")[:200]
    items = []
    for it in items_qs:
        hours = round((it.duration_minutes or 0) / 60.0, 2)
        items.append({"obj": it, "hours": hours})
    return render(request, "worklog/work_list.html", {"items": items})

@login_required
def work_delete(request, pk):
    item = get_object_or_404(WorkEntry, pk=pk, user=request.user)
    item.delete()
    return redirect("work_list_create")
