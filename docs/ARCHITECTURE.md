
# **智见航语（ZhiJian-AeroNLP）系统架构（MVP）**

## 一、总体概述（Overview）

**智见航语（ZhiJian-AeroNLP）** 是一个面向航空情报场景的智能解析与态势感知系统。本阶段为 **MVP（最小可行产品）**，重点在于完成基础系统能力搭建、核心接口定义以及后续功能的可扩展架构设计。

* **后端（Backend）**

  * 技术栈：FastAPI + SQLModel
  * 核心能力：

    * JWT 用户认证
    * 基于角色的权限控制（RBAC）
    * 操作审计日志
    * 请求限流（内存级占位实现，后续可扩展为 Redis）

* **前端（Frontend）**

  * 技术栈：Vue 3 + Vite + TypeScript
  * 状态管理：Pinia
  * 路由管理：Vue Router
  * UI 组件库：Naive UI

* **基础设施（Infrastructure）**

  * Docker Compose 统一编排
  * 服务组成：

    * PostgreSQL（业务数据存储）
    * Redis（缓存 / 会话 / 后续限流扩展）
    * 后端服务（FastAPI）
    * 前端服务（Vue3）

---

## 二、后端模块设计（Backend Modules）

后端采用 **分层模块化设计**，保证代码可维护性与功能解耦。

### 1. `app/core`（核心基础模块）

负责系统级能力的统一封装：

* 配置管理（Config）
* 日志系统（Logging）
* 统一异常与错误处理
* 安全相关组件（JWT、密码加密）
* 请求限流机制（MVP 阶段为内存实现）
* 权限控制与角色管理（RBAC）

### 2. `app/db`（数据访问层）

* SQLModel 数据库模型定义
* 数据库 Session 管理
* 与 PostgreSQL 的统一交互入口

### 3. `app/api`（接口层）

* 路由统一注册
* RESTful API 接口定义
* 请求与响应模型（Schema）
* 权限校验与依赖注入

### 4. `app/services`（业务服务层）

* NOTAM 智能解析服务（当前为 Stub，占位实现）
* 操作审计日志记录服务
* 后续可扩展为：

  * 影响分析
  * 告警生成
  * 多模型协同推理等

---

## 三、前端模块设计（Frontend Modules）

前端以 **功能视图为中心**，便于后续业务模块快速扩展。

### 1. `LoginView.vue`

* 用户登录与注册界面
* 表单校验
* JWT 获取与状态初始化

### 2. `HomeView.vue`

* 系统仪表盘入口
* 核心功能模块导航
* 关键状态与统计信息汇总展示

### 3. `PlaceholderView.vue`

* 功能占位视图
* 用于尚未实现模块的页面骨架
* 保证路由与导航结构的完整性

---

## 四、MVP 接口清单（API Endpoints）

### 1. 认证与用户相关

* `POST /api/v1/auth/register`：用户注册
* `POST /api/v1/auth/login`：用户登录
* `POST /api/v1/auth/refresh`：刷新访问令牌
* `POST /api/v1/auth/logout`：用户登出

### 2. NOTAM 智能解析

* `POST /api/v1/notam/parse`：NOTAM 文本解析
* `GET /api/v1/notam/history`：历史解析记录查询

### 3. 仪表盘与任务

* `GET /api/v1/dashboard/summary`：仪表盘数据汇总
* `GET /api/v1/tasks`：任务列表接口

### 4. 系统与平台能力

* `GET /api/v1/api-keys`：API Key 管理（预留）
* `GET /health`：系统健康检查接口

---

## 五、架构设计说明（MVP 原则）

* **接口先行**：优先稳定 API 结构，内部实现可快速迭代
* **模块解耦**：业务逻辑集中在 `services`，避免 API 层膨胀
* **可扩展性**：

  * 限流、缓存、审计等均预留 Redis 扩展点
  * NOTAM 解析模块可平滑升级为多模型 / 多策略体系
* **工程可落地**：保证比赛展示、Demo 演示、功能扩展三者平衡

---