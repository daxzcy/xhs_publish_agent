# 小红书 AI 发布助手

输入主题，AI 自动生成选题、文案、封面图，一键发布到小红书。

## 技术栈

- **后端**：FastAPI + Tortoise ORM + MySQL
- **前端**：Vue 3 + Vite + Element Plus
- **AI**：DeepSeek（文案）+ 通义千问（图片生成）
- **存储**：阿里云 OSS
- **自动化**：Playwright（小红书签名）

## 核心功能

- 输入主题 → AI 生成板块和标题
- AI 生成小红书文案
- AI 生成封面图
- 素材库管理（文案 + 图片增删改查）
- 多账号发布
- 发布历史记录

## 快速开始

### 后端

```bash
cd flask_api_operation
uv sync
uv run python main.py
```

### 前端

```bash
cd vue_operation
pnpm install
pnpm dev
```

## 环境变量

复制 `.env.example` 为 `.env`，填入：

- `DEEPSEEK_API_KEY` — DeepSeek API
- `QWEN_KEY` — 通义千问（图片生成）
- `OSS_*` — 阿里云 OSS
- `DB_*` — MySQL

## 数据库

```bash
mysql -u root -p xhs_operation < app/operation.sql
```
