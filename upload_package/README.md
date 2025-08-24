# WorkReport MVP (Django)

- 邮箱注册/登录、自定义用户模型；
- 工作日报（日期+时间段），自动计算时长；
- 首页统计以**小时**展示，新增“趋势”Tab；
- AI 汇报（DeepSeek / OpenAI），Markdown 结果下载；
- Arco 风格轻量样式：`static/arco-lite.css` + `static/arco-lite.js`。

## 运行
```
python -m venv .venv
# PowerShell 需要：Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 文档
- 架构说明（Mermaid 图）：`docs/architecture.md`


## UI 更新
- 采用 Arco 风格主题（深色科技感），位于 `static/css/arco-theme.css`
- 首页新增 Tab：概览/按日/趋势
- 时长以**小时**展示；新增**时间段**控件自动换算
