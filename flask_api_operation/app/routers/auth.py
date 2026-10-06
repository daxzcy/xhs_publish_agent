"""登录认证：校验用户名密码，返回 JWT（密码明文比对，不加密）。"""
import logging
import time
import jwt

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from tortoise.exceptions import DoesNotExist

from app.config import JWT_SECRET, JWT_ALGORITHM, JWT_ACCESS_EXPIRE_SECONDS
from app.models import User

# 日志记录器，用于记录错误日志
logger = logging.getLogger(__name__)

# 创建子路由，后续挂载到主路由
router = APIRouter()

# 从 Authorization: Bearer <token> 请求头中提取令牌（不验证签名）
# auto_error=False：缺失/格式错误时返回 None，由下游 Depends 自行处理
security = HTTPBearer(auto_error=False)

# 定义登录请求的模型
class LoginBody(BaseModel):
    userName: str
    password: str

# 生成 token
def _make_token(sub : str , exp_seconds : int) -> str:
    # token包含的信息：用户ID（sub），签发时间，过期时间
    payload = {
        "sub": sub,
        "iat": time.time(),
        "exp": time.time() + exp_seconds,
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# 登录接口
@router.post("/login")
async def login(body: LoginBody):
    # 校验用户名密码，用户名和密码不为空
    username = (body.userName or "").strip()
    if not username:
        return {"code": 400, "message": "请输入用户名", "data":None}
    if not body.password:
        return {"code": 400, "message": "请输入密码", "data":None}

    # 查询用户
    try:
        user = await User.get(username=username)
    except DoesNotExist:
        return {"code": 401, "message": "用户名或密码错误", "data":None}
    
    # 匹配密码
    if user.password != body.password:
        return {"code": 401, "message": "用户名或密码错误", "data":None}

    # 生成token
    try:
        user_id = str(user.id)
        access_token = _make_token(user_id, JWT_ACCESS_EXPIRE_SECONDS)
        user_name = getattr(user, "name", None) or user.username
        return {
            "code": 200, 
            "message": "登录成功", 
            "data":{
                "userId":user_id,
                "userName": user_name,
                "accessToken": access_token # 令牌
            }
        }
    except Exception as e:
        logger.exception("登录生成 token 失败：%s", e)
        return {"code": 500, "message": "服务异常，请稍后再试", "data":None}
        

# 鉴权函数，解析JWT令牌
async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> int:
    # 如果请求头没有携带令牌，直接抛出 401 异常
    if not credentials or credentials.credentials is None:
        raise HTTPException(status_code=401, detail="未登录或 token 无效")

    # 解析令牌，如果解析失败，抛出 401 异常
    try:
        payload = jwt.decode(
            credentials.credentials, # 令牌
            JWT_SECRET, # 密钥
            algorithms=[JWT_ALGORITHM], # 算法
        )
        # 获取用户id
        sub = payload.get("sub")
        # 如果用户id为空，抛出 401 异常
        if not sub:
            raise HTTPException(status_code=401, detail="无效的令牌")
        # 返回用户id
        return int(sub)
    except Exception as e:
        logger.exception("解析令牌失败：%s", e)
        raise HTTPException(status_code=401, detail="无效的令牌或者令牌已过期") 