import os, requests
from django.conf import settings

def _build_prompt(entries, granularity, start_date, end_date, extra_prompt=""):
    lines = [
        "你是我的职场助理，请根据以下工作记录生成清晰、有条理、适合向领导汇报的总结性工作汇报。",
        f"时间范围：{start_date} 至 {end_date}；粒度：{granularity}",
        "请输出：",
        "1) 概要（3-6条要点，带数据）；",
        "2) 本期关键成果（条目列表，含量化指标/影响）；",
        "3) 遇到的问题与风险（含原因与解决建议）；",
        "4) 下阶段计划与资源需求；",
        "5) 附：本期工作明细（按日期简单归类）",
    ]
    if extra_prompt:
        lines.append(f"补充偏好：{extra_prompt}")
    lines.append("\n【工作明细】")
    for e in entries:
        mins = e.get('duration_minutes') or 0
        hrs = round(mins / 60.0, 2)
        lines.append(f"- {e['date']} | {e.get('title') or ''} | {hrs} 小时 | {e['content']}".strip())
    return "\n".join(lines)

def generate_report(entries, granularity, start_date, end_date, extra_prompt="", user=None):
    """
    生成AI汇报
    
    Args:
        entries: 工作记录列表
        granularity: 汇报粒度
        start_date: 开始日期
        end_date: 结束日期
        extra_prompt: 额外提示
        user: 用户对象（用于获取API配置）
    """
    # 获取API配置
    if user:
        from ..models import APIConfig
        api_config = APIConfig.objects.filter(user=user, is_active=True).first()
        if api_config:
            provider = api_config.provider
            api_key = api_config.api_key
            api_base = api_config.api_base
        else:
            raise ValueError("未找到已启用的API配置，请先在API管理中配置并启用一个API")
    else:
        # 回退到系统配置
        provider = settings.LLM_PROVIDER
        api_key = getattr(settings, f"{provider.upper()}_API_KEY", "")
        api_base = getattr(settings, f"{provider.upper()}_API_BASE", "")

    prompt = _build_prompt(entries, granularity, start_date, end_date, extra_prompt)

    if provider == "openai":
        try:
            from openai import OpenAI
            # 检查是否使用LLMHub代理
            if api_base and "llmhub" in api_base.lower():
                if not api_base.endswith('/v1'):
                    api_base = api_base.rstrip('/') + '/v1'
            
            client = OpenAI(
                api_key=api_key,
                base_url=api_base if api_base else None
            )
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个严谨的中文职场报告助理。输出Markdown，结构化清晰。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            if hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                raise ValueError(f"OpenAI API响应格式错误: {type(response)} - {response}")
        
        except Exception as e:
            error_msg = str(e)
            # 针对LLMHub的特殊错误处理
            if "llmhub" in (api_base or "").lower():
                if "<!DOCTYPE html>" in error_msg:
                    raise ValueError(f"LLMHub代理服务返回了网页而非API响应，可能原因：\n1. API Key无效或已过期\n2. 账户余额不足\n3. API端点配置错误\n请检查API Key: {api_key[:10]}...")
                elif "401" in error_msg or "Unauthorized" in error_msg:
                    raise ValueError(f"LLMHub API Key认证失败: {api_key[:10]}...，请检查API Key是否正确")
                elif "403" in error_msg or "Forbidden" in error_msg:
                    raise ValueError(f"LLMHub访问被拒绝，可能是余额不足或账户被限制")
                else:
                    raise ValueError(f"LLMHub代理服务调用失败: {str(e)}")
            else:
                raise ValueError(f"OpenAI API调用失败: {str(e)}")

    elif provider == "deepseek":
        try:
            url = f"{api_base}/chat/completions" if api_base else "https://api.deepseek.com/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个严谨的中文职场报告助理。输出Markdown，结构化清晰。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except Exception as e:
            raise ValueError(f"DeepSeek API调用失败: {str(e)}")

    elif provider == "claude":
        try:
            url = f"{api_base}/messages" if api_base else "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["content"][0]["text"]
        
        except Exception as e:
            raise ValueError(f"Claude API调用失败: {str(e)}")

    else:
        raise ValueError(f"不支持的LLM提供商: {provider}")
