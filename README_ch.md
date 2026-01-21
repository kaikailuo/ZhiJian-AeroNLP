# NOTAM 解析系统

## 重构架构图（仅本次重构）

```text
重构后目录结构（仅本次重构）

├── apps
│   ├── backend                     # 后端 FastAPI 服务
│   │   ├── app
│   │   │   ├── api                  # API 路由注册与版本入口
│   │   │   │   └── routes           # 具体业务接口（auth/notam/dashboard/tasks……）
│   │   │   ├── core                 # 配置/日志/错误/安全/限流
│   │   │   ├── db                   # SQLModel 数据模型与会话
│   │   │   ├── schemas              # Pydantic 请求/响应模型
│   │   │   ├── services             # 业务服务层（解析/审计等）
│   │   │   └── scripts              # 种子数据/初始化脚本
│   │   ├── pyproject.toml           # 后端依赖（uv）
│   │   └── requirements.txt         # 运行依赖清单
│   └── frontend                     # 前端 Vue3 应用
│       ├── src
│       │   ├── assets               # 全局样式/静态资源
│       │   ├── services             # API 封装（auth/notam/...）
│       │   ├── stores               # Pinia 状态管理
│       │   ├── views                # 页面（登录/首页/占位模块）
│       │   └── router               # 路由配置
│       ├── package.json             # 前端依赖
│       └── vite.config.ts           # Vite 构建配置
├── infra
│   └── docker-compose.yml           # 一键启动前后端 + DB + Redis
├── docs
│   └── demos                        # 演示脚本（登录/解析/看板）
└── .env.example                     # 环境变量模板
```

## 整体架构说明

当前仓库包含两层：

1) **研究解析流水线（保留）**  
   - CLI 解析流程与 Streamlit 演示。  
   - 核心文件：`main.py`, `streamlit_app.py`, `src/`, `config/`。

2) **产品 MVP 平台（新增）**  
   - **后端**：FastAPI + SQLModel + JWT + RBAC + 审计日志  
     - 入口：`apps/backend/app/main.py`  
     - 核心：`apps/backend/app/core`（配置/日志/错误/安全）  
     - 数据模型：`apps/backend/app/db/models.py`  
     - API 路由：`apps/backend/app/api/routes/*`  
   - **前端**：Vue3 + Vite + TypeScript + Pinia + Router + Naive UI  
     - 入口：`apps/frontend/src/main.ts`  
     - 页面：`apps/frontend/src/views/*`（登录 + 首页 + 占位模块）  
   - **基础设施**：Docker Compose 本地一键运行  
     - `infra/docker-compose.yml`

## MVP 重构（新应用结构）

仓库已新增 ZhiJian-AeroNLP 平台的 MVP 骨架：

- 后端：`apps/backend`（FastAPI + SQLModel + JWT + RBAC + 审计日志）
- 前端：`apps/frontend`（Vue3 + Vite + TypeScript + Pinia + Naive UI）
- 部署：`infra/docker-compose.yml`
- 文档：`docs/ARCHITECTURE.md` 与 `docs/demos/*`

### 快速启动

```bash
#vscode
Ctrl+shift+P -> Task: Run Task -> dev:all:with-deps
# 用其他编译器的需要自己配置一下
```

- 后端: http://localhost:8000/docs
- 前端: http://localhost:5173

### 本地开发

```bash
# 后端
cd apps/backend
uv venv
uv sync
uv run uvicorn app.main:app --reload --port 8000

# 前端
cd apps/frontend
npm install
npm run dev
```

### 演示脚本

```bash
pwsh docs/demos/01_auth_and_parse.ps1
pwsh docs/demos/02_dashboard.ps1
pwsh docs/demos/03_tasks.ps1
```

原有 NOTAM 解析流程（CLI + Streamlit）仍保留在根目录下，
可继续独立使用（`main.py`、`streamlit_app.py`）。
