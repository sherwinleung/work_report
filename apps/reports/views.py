from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from datetime import date, timedelta
from apps.worklog.models import WorkEntry
from .models import Report
from .services.ai_client import generate_report

@login_required
def report_list(request):
    items = Report.objects.filter(user=request.user).order_by("-created_at")[:100]
    return render(request, "reports/report_list.html", {"items": items})

@login_required
def report_generate(request):
    if request.method == "POST":
        granularity = request.POST.get("granularity","custom")
        start_date = date.fromisoformat(request.POST.get("start_date"))
        end_date = date.fromisoformat(request.POST.get("end_date"))
        extra_prompt = request.POST.get("prompt_prefs","")

        entries_qs = WorkEntry.objects.filter(user=request.user, date__range=(start_date, end_date))                        .values("date","title","content","duration_minutes").order_by("date","id")
        entries = list(entries_qs)

        rep = Report.objects.create(user=request.user, granularity=granularity,
                                    start_date=start_date, end_date=end_date,
                                    prompt_prefs=extra_prompt, status="RUNNING")

        try:
            content = generate_report(entries, granularity, start_date, end_date, extra_prompt)
            rep.content_md = content
            rep.status = "DONE"
            rep.save()
        except Exception as e:
            rep.content_md = f"生成失败：{e}"
            rep.status = "ERROR"
            rep.save()

        return redirect("report_detail", pk=rep.pk)

    today = date.today()
    start = today - timedelta(days=today.weekday())
    end = today
    return render(request, "reports/report_generate.html", {
        "default_start": start, "default_end": end
    })

@login_required
def report_detail(request, pk):
    rep = get_object_or_404(Report, pk=pk, user=request.user)
    if request.GET.get("download") == "md":
        resp = HttpResponse(rep.content_md, content_type="text/markdown; charset=utf-8")
        filename = f"report_{rep.start_date}_{rep.end_date}.md"
        resp["Content-Disposition"] = f"attachment; filename={filename}"
        return resp
    return render(request, "reports/report_detail.html", {"rep": rep})
