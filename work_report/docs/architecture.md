# 系统架构说明

本文档用 Mermaid 图展示项目的组件结构、关键流程、数据模型与路由映射。

## 架构总览
```mermaid
flowchart TD
    A[浏览器\nBootstrap 页面] -->|HTTP| B(Django 5 应用)

    subgraph PROJ[workreport 项目]
      G[settings.py\nAUTH_USER_MODEL\nREST_FRAMEWORK\nLLM_PROVIDER] --> J[.env 环境变量]
      F[templates:\nbase, accounts, worklog, reports]

      subgraph ACC[apps.accounts]
        ACC1[models.User\n(邮箱登录)]
        ACC2[views:\nregister, user_list]
        ACC3[urls:\n/accounts/...]
      end

      subgraph WL[apps.worklog]
        WL1[models.WorkEntry]
        WL2[views:\ndashboard, work_list_create, work_delete]
        WL3[urls:\n/dashboard, /work, /work/&lt;id&gt;/delete]
      end

      subgraph REP[apps.reports]
        REP1[models.Report]
        REP2[views:\nreport_generate, report_detail, report_list]
        REP3[services/ai_client.py\n(DeepSeek / OpenAI)]
        REP2 --> REP3
      end
    end

    B -->|ORM| H[(SQLite: db.sqlite3)]
    REP3 -->|HTTP JSON| L[LLM Provider\nDeepSeek 或 OpenAI]
```

## 关键流程：AI 汇报生成
```mermaid
sequenceDiagram
    participant U as 用户（浏览器）
    participant V as reports.views
    participant W as WorkEntry(ORM)
    participant R as Report(ORM)
    participant S as ai_client
    participant L as LLM Provider

    U->>V: POST /reports/generate\n(粒度/起止日期/偏好)
    V->>W: 查询 WorkEntry（用户+时间段）
    W-->>V: 返回工作明细列表
    V->>R: 创建 Report(status="RUNNING")
    V->>S: generate_report(entries, dates, prefs)
    S->>L: Chat API 请求（JSON）
    L-->>S: 返回 Markdown 汇报
    S-->>V: content_md
    V->>R: 更新 Report(status="DONE", content_md)
    V-->>U: 302 -> /reports/{id}
    U->>V: GET /reports/{id}
    V-->>U: 展示 Markdown（可下载 .md）
```

## 数据模型（ER）
```mermaid
erDiagram
    USER ||--o{ WORKENTRY : "1:N"
    USER ||--o{ REPORT    : "1:N"

    USER {
      int id PK
      string email "唯一登录名"
      string password_hash
      string first_name
      string last_name
      boolean is_active
      boolean is_staff
      boolean is_superuser
      datetime date_joined
      datetime last_login
    }

    WORKENTRY {
      int id PK
      int user_id FK
      date date
      time start_time
      time end_time
      string title
      text content
      int duration_minutes
      datetime created_at
      datetime updated_at
    }

    REPORT {
      int id PK
      int user_id FK
      string granularity  "daily/weekly/monthly/yearly/custom"
      date start_date
      date end_date
      text prompt_prefs
      text content_md
      string status     "PENDING/RUNNING/DONE/ERROR"
      datetime created_at
    }
```

## 路由与视图映射
```mermaid
flowchart LR
    ROOT[/ / -> /dashboard /]

    ROOT --> B[/ /dashboard /] --> Bv[worklog.dashboard]
    ROOT --> C[/ /work /] --> Cv[worklog.work_list_create]
    ROOT --> D[/ /work/&lt;id&gt;/delete /] --> Dv[worklog.work_delete]

    ROOT --> E[/ /reports/ /] --> Ev[reports.report_list]
    ROOT --> F[/ /reports/generate /] --> Fv[reports.report_generate]
    ROOT --> G[/ /reports/&lt;id&gt;/ /] --> Gv[reports.report_detail]

    ROOT --> H[/ /accounts/login /] --> Hv[内置 LoginView]
    ROOT --> I[/ /accounts/register /] --> Iv[accounts.register]
    ROOT --> J[/ /accounts/logout /] --> Jv[内置 LogoutView]

    ROOT --> K[/ /admin/ /] --> Kv[Django Admin]
```
