# 启动项目
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import v1_router,auth_router
from app.database import register_db
from app.config import TORTOISE_ORM
import uvicorn

# 创建FastAPI实例
app = FastAPI()

# 添加跨域请求CORS中间件
app.add_middleware(
    CORSMiddleware,
    # 允许跨域的前端地址
    allow_origins=["http://127.0.0.1:5173"],
    # 允许携带Cookie
    allow_credentials=True,
    # 允许的请求方法
    allow_methods=["*"],
    # 允许的请求头
    allow_headers=["*"],
)

# 注册路由
app.include_router(v1_router)
app.include_router(auth_router)

# 连接数据库
register_db(app ,TORTOISE_ORM , generate_schemas=False)

# 启动项目
if __name__ == "__main__":
    uvicorn.run('main:app' , host="127.0.0.1" , port=8000 , reload=True)