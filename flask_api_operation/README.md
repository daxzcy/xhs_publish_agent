# 智能运营平台 - 后端

AI 驱动的小红书内容运营平台后端 API 服务，提供用户认证、AI 内容生成、图片管理与发布等接口。

## 功能

- 🔐 用户认证 — JWT 登录鉴权
- 🤖 Coze 智能体集成 — 选题生成与文案创作
- 🎨 通义千问图像生成 — AI 封面图生成
- ☁️ 阿里云 OSS — 图片上传与存储
- 📊 数据管理 — 板块、标题、发布记录 CRUD
- 🚀 小红书发布 — Puppeteer 浏览器自动化

## 技术栈

| 类别    | 技术                             |
| ------- |--------------------------------|
| 框架    | FastAPI                        |
| ORM     | Tortoise ORM                   |
| 数据库  | MySQL                          |
| 认证    | PyJWT（HS256）                   |
| AI 服务 | deepseek + 阿里云 DashScope（通义千问） |
| 存储    | 阿里云 OSS                        |
| 迁移    | Aerich                         |
| 包管理  | uv                             |

## 快速开始

### 环境要求

- Python >= 3.10
- MySQL 数据库
- uv 包管理器

### 安装

```bash
# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入实际配置
```

### 配置环境变量

```env
# 数据库
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=xhs_operation

# JWT
JWT_SECRET=your-secret-key-change-in-production

# Coze 智能体
COZE_TOKEN=your_coze_token
BOT_ID_TOPIC=your_topic_bot_id        # 选题机器人
BOT_ID_CONTENT=your_content_bot_id     # 文案创作机器人
USER_ID=your_coze_user_id

# 通义千问（DashScope）
QWEN_KEY=your_qwen_api_key

# 阿里云 OSS
OSS_ACCESS_KEY_ID=your_access_key
OSS_ACCESS_KEY_SECRET=your_secret
OSS_REGION=ap-southeast-1
OSS_BUCKET=your_bucket_name
OSS_ENDPOINT=your_bucket_endpoint
```

### 数据库迁移

```bash
# 生成迁移文件
uv run aerich migrate

# 执行迁移
uv run aerich upgrade
```

### 运行

```bash
# 开发模式（热重载）
uv run python main.py

# 服务启动在 http://0.0.0.0:8000
```

## 目录结构

```
flask_api_operation/
├── main.py                 # 应用入口，FastAPI 实例创建
├── app/
│   ├── config.py           # 配置（数据库、JWT、Tortoise ORM）
│   ├── database.py         # Tortoise ORM 生命周期管理
│   ├── agent/
│   │   ├── coze_agent.py   # Coze 智能体调用（选题 + 文案）
│   │   └── qwen_agent.py   # 通义千问图片生成
│   ├── models/
│   │   └── __init__.py     # 数据模型定义（User/Section/Title/...）
│   ├── routers/
│   │   ├── __init__.py     # 路由注册（v1 + auth）
│   │   ├── auth.py         # 登录认证接口
│   │   ├── create.py       # 创作相关接口（选题/文案/风格）
│   │   └── test.py         # 测试接口
│   └── util/
│       └── upload.py       # 阿里云 OSS 图片上传
├── migrations/             # Aerich 数据库迁移文件
├── pyproject.toml          # 项目依赖配置
└── uv.lock                 # 依赖锁定文件
```

## API 接口

### 认证

| 方法 | 路径       | 说明               |
| ---- | ---------- | ------------------ |
| POST | `/login` | 用户登录，返回 JWT |

### 创作流程（均需 Bearer Token）

| 方法 | 路径                        | 说明                                |
| ---- | --------------------------- | ----------------------------------- |
| POST | `/v1/create/start`        | 根据主题生成板块与标题（调用 Coze） |
| GET  | `/v1/create/themes`       | 搜索已有主题列表                    |
| GET  | `/v1/create/load`         | 按主题加载板块与标题                |
| GET  | `/v1/create/title/{id}`   | 查询标题详情                        |
| POST | `/v1/create/copy`         | 根据标题生成文案（调用 Coze）       |
| POST | `/v1/create/save-copy`    | 保存/更新文案                       |
| POST | `/v1/create/cover`        | 生成封面图（调用通义千问）          |
| POST | `/v1/create/image/upload` | 上传正文图片                        |
| PUT  | `/v1/create/title/{id}`   | 更新标题信息                        |
| GET  | `/v1/create/styles`       | 获取风格列表                        |
| GET  | `/v1/create/models`       | 获取 AI 模型列表                    |

### 素材库

| 方法   | 路径                          | 说明             |
| ------ | ----------------------------- | ---------------- |
| GET    | `/v1/material/images`       | 获取图片素材列表 |
| POST   | `/v1/material/image/upload` | 上传图片素材     |
| DELETE | `/v1/material/image/{id}`   | 删除图片素材     |
| GET    | `/v1/material/copies`       | 获取文案素材列表 |

### 发布与记录

| 方法 | 路径                                         | 说明             |
| ---- | -------------------------------------------- | ---------------- |
| POST | `/v1/create/publish-xiaohongshu`           | 发布到小红书     |
| POST | `/v1/records/create_publish_records`       | 创建发布记录     |
| GET  | `/v1/records/list`                         | 获取发布记录列表 |
| GET  | `/v1/publish_images/get_publish_images`    | 获取发布图片     |
| POST | `/v1/publish_images/create_publish_images` | 关联发布图片     |

## AI 服务流程

```
POST /v1/create/start
  └─ Coze BOT_ID_TOPIC → 解析 JSON → 写入 Section + Title 表

POST /v1/create/copy
  └─ Coze BOT_ID_CONTENT → 更新 Title.content

POST /v1/create/cover
  └─ 通义千问 qwen-image-2.0-pro → 生成图片 → 写入 TitleImage 表

POST /v1/create/publish-xiaohongshu
  └─ Puppeteer 打开小红书创作者中心 → 模拟填写发布
```

## 数据模型

| 表名                  | 说明                                   |
| --------------------- | -------------------------------------- |
| `t_users`           | 用户表                                 |
| `t_sections`        | 板块表（用户 + 主题 → 板块）          |
| `t_titles`          | 标题表（板块 → 标题 + 文案 + 状态）   |
| `t_title_images`    | 标题图片表（封面图 / 正文图 / 缩略图） |
| `t_style`           | 风格表（图片生成 prompt 模板）         |
| `t_models`          | AI 模型注册表                          |
| `t_publish_records` | 发布记录表                             |
| `t_publish_images`  | 发布图片关联表                         |

## 注意事项

- 密码目前以明文存储，生产环境应改为哈希加盐。
- Coze 智能体返回的 JSON 包裹在 markdown 代码块中，`create.py` 的 `_extract_json()` 会自动剥离。
- 图片上传走阿里云 OSS，生成随机文件名存储于 `images/` 路径下。
