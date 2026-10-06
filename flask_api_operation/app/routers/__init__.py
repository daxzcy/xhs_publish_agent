from fastapi import APIRouter

# 从 app/routers/ 目录下导入所有子路由模块
from app.routers import (
    auth,
    create,
    material,
    history,
    records,
    publish_images,
    xhs,
)

# 创建一个主路由器 v1_router，专门挂载所有 v1 版本的 API
# 所有在这个 router 里的接口都会自动加 /v1 前缀
v1_router = APIRouter(prefix="/v1", tags=["v1"])

# 注册各子路由
v1_router.include_router(create.router)
v1_router.include_router(material.router)
v1_router.include_router(history.router)
v1_router.include_router(records.router)
v1_router.include_router(publish_images.router)
v1_router.include_router(xhs.router)

# 登录路由器，挂载登录接口（不带 /v1 前缀）
auth_router = APIRouter(tags=["auth"])
auth_router.include_router(auth.router)