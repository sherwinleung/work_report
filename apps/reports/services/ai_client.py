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

def generate_report(entries, granularity, start_date, end_date, extra_prompt=""):
    provider = settings.LLM_PROVIDER
    prompt = _build_prompt(entries, granularity, start_date, end_date, extra_prompt)

    if provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        resp = client.responses.create(model="gpt-4o-mini", input=prompt)
        return resp.output_text

    elif provider == "deepseek":
        url = settings.DEEPSEEK_API_BASE.rstrip("/") + "/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"}
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个严谨的中文职场报告助理。输出Markdown，结构化清晰。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
        }
        r = requests.post(url, headers=headers, json=data, timeout=120)
        r.raise_for_status()
        j = r.json()
        return j["choices"][0]["message"]["content"]

    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}")
