from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from datetime import date, timedelta
from apps.worklog.models import WorkEntry
from .models import Report, APIConfig
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
            content = generate_report(entries, granularity, start_date, end_date, extra_prompt, user=request.user)
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

@login_required
def api_management(request):
    """
    API管理页面 - 管理用户的大模型API配置
    """
    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "save_config":
            # 保存或更新API配置
            provider = request.POST.get("provider")
            api_key = request.POST.get("api_key")
            api_base = request.POST.get("api_base", "")
            
            if not provider or not api_key:
                messages.error(request, "提供商和API密钥不能为空")
                return redirect("api_management")
            
            config, created = APIConfig.objects.get_or_create(
                user=request.user,
                provider=provider,
                defaults={'api_key': api_key, 'api_base': api_base}
            )
            
            if not created:
                config.api_key = api_key
                config.api_base = api_base
                config.save()
            
            messages.success(request, f"{'创建' if created else '更新'}了 {provider} API配置")
            return redirect("api_management")
        
        elif action == "activate":
            # 激活指定的API配置
            config_id = request.POST.get("config_id")
            try:
                config = APIConfig.objects.get(id=config_id, user=request.user)
                config.is_active = True
                config.save()  # save方法会自动禁用其他配置
                messages.success(request, f"已启用 {config.provider} API配置")
            except APIConfig.DoesNotExist:
                messages.error(request, "API配置不存在")
            return redirect("api_management")
        
        elif action == "delete":
            # 删除API配置
            config_id = request.POST.get("config_id")
            try:
                config = APIConfig.objects.get(id=config_id, user=request.user)
                provider_name = config.provider
                config.delete()
                messages.success(request, f"已删除 {provider_name} API配置")
            except APIConfig.DoesNotExist:
                messages.error(request, "API配置不存在")
            return redirect("api_management")
    
    # GET请求 - 显示API管理页面
    configs = APIConfig.objects.filter(user=request.user).order_by('-updated_at')
    active_config = configs.filter(is_active=True).first()
    
    # 所有可用的提供商
    all_providers = [
        {'key': 'openai', 'name': 'OpenAI'},
        {'key': 'deepseek', 'name': 'DeepSeek'},
        {'key': 'claude', 'name': 'Claude'},
    ]
    
    # 已配置的提供商
    existing_providers = set(configs.values_list('provider', flat=True))
    
    return render(request, "reports/api_management.html", {
        "configs": configs,
        "active_config": active_config,
        "all_providers": all_providers,
        "existing_providers": existing_providers,
    })

@login_required
def test_api_connection(request):
    """
    测试API连接
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "只支持POST请求"})
    
    provider = request.POST.get("provider")
    api_key = request.POST.get("api_key")
    api_base = request.POST.get("api_base", "")
    
    if not provider or not api_key:
        return JsonResponse({"success": False, "message": "提供商和API密钥不能为空"})
    
    try:
        test_prompt = "Hello, this is a test message. Please respond with 'API connection successful'."
        
        if provider == "openai":
            import openai
            # 检查是否使用LLMHub代理
            if api_base and "llmhub" in api_base.lower():
                if not api_base.endswith('/v1'):
                    api_base = api_base.rstrip('/') + '/v1'
            
            client = openai.OpenAI(
                api_key=api_key,
                base_url=api_base if api_base else None
            )
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": test_prompt}],
                max_tokens=50
            )
            
            if hasattr(response, 'choices') and len(response.choices) > 0:
                success_msg = "OpenAI API连接成功"
                if "llmhub" in (api_base or "").lower():
                    success_msg = "LLMHub代理服务连接成功"
                return JsonResponse({"success": True, "message": success_msg})
            else:
                return JsonResponse({"success": False, "message": f"API响应格式错误: {type(response)}"})
        
        elif provider == "deepseek":
            import requests
            url = f"{api_base}/chat/completions" if api_base else "https://api.deepseek.com/chat/completions"
            
            response = requests.post(url, json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": test_prompt}],
                "max_tokens": 50
            }, headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }, timeout=30)
            
            if response.status_code == 200:
                return JsonResponse({"success": True, "message": "DeepSeek API连接成功"})
            else:
                return JsonResponse({"success": False, "message": f"DeepSeek API连接失败: {response.status_code} {response.text}"})
        
        elif provider == "claude":
            import requests
            url = f"{api_base}/messages" if api_base else "https://api.anthropic.com/v1/messages"
            
            response = requests.post(url, json={
                "model": "claude-3-haiku-20240307",
                "max_tokens": 50,
                "messages": [{"role": "user", "content": test_prompt}]
            }, headers={
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }, timeout=30)
            
            if response.status_code == 200:
                return JsonResponse({"success": True, "message": "Claude API连接成功"})
            else:
                return JsonResponse({"success": False, "message": f"Claude API连接失败: {response.status_code} {response.text}"})
        
        else:
            return JsonResponse({"success": False, "message": f"不支持的提供商: {provider}"})
    
    except Exception as e:
        error_msg = str(e)
        # 针对LLMHub的特殊错误处理
        if provider == "openai" and "llmhub" in (api_base or "").lower():
            if "<!DOCTYPE html>" in error_msg:
                return JsonResponse({"success": False, "message": f"LLMHub代理服务返回了网页而非API响应，可能原因：\n1. API Key无效或已过期\n2. 账户余额不足\n3. API端点配置错误\n请检查API Key: {api_key[:10]}..."})
            elif "401" in error_msg or "Unauthorized" in error_msg:
                return JsonResponse({"success": False, "message": f"LLMHub API Key认证失败: {api_key[:10]}...，请检查API Key是否正确"})
            elif "403" in error_msg or "Forbidden" in error_msg:
                return JsonResponse({"success": False, "message": f"LLMHub访问被拒绝，可能是余额不足或账户被限制"})
            else:
                return JsonResponse({"success": False, "message": f"LLMHub代理服务调用失败: {str(e)}"})
        else:
            return JsonResponse({"success": False, "message": f"连接失败: {str(e)}"})
