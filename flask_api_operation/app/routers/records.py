"""
发布记录模块 - 管理发布记录的创建和查询
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.models import PublishRecord, Title, Section
from app.routers.auth import get_current_user_id

router = APIRouter(prefix="/records", tags=["records"])


class CreatePublishRecordRequest(BaseModel):
    title_id: int
    platform: int  # 1=小红书，2=抖音，3=快手，4=微信公众号
    content: Optional[str] = None
    publish_status: Optional[int] = 0  # 0=待发布，1=发布中，2=成功，3=失败，4=已删除


class UpdatePublishRecordRequest(BaseModel):
    publish_status: Optional[int] = None
    content: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    share_count: Optional[int] = None


@router.post("/create_publish_records")
async def create_publish_record(
    body: CreatePublishRecordRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    创建发布记录
    """
    # 验证标题是否存在
    title = await Title.get_or_none(id=body.title_id)
    if not title:
        return {"code": 404, "message": "标题不存在", "data": None}

    # 验证平台
    if body.platform not in [1, 2, 3, 4]:
        return {"code": 400, "message": "平台类型无效，必须是1(小红书)、2(抖音)、3(快手)或4(微信公众号)", "data": None}

    # 验证发布状态
    if body.publish_status not in [0, 1, 2, 3, 4]:
        return {"code": 400, "message": "发布状态无效", "data": None}

    # 创建发布记录
    record = await PublishRecord.create(
        user_id=user_id,
        title_id=body.title_id,
        platform=body.platform,
        content=body.content,
        publish_status=body.publish_status,
        publish_time=datetime.now() if body.publish_status == 2 else None,
        created_at=datetime.now()
    )

    # 如果发布成功，更新标题状态
    if body.publish_status == 2:
        title.status = "2"  # 已发布
        await title.save()

    return {
        "code": 200,
        "message": "创建成功",
        "data": {
            "id": record.id,
            "title_id": record.title_id,
            "platform": record.platform,
            "publish_status": record.publish_status,
            "created_at": record.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    }


@router.get("/list")
async def get_records_list(
    title_id: Optional[int] = Query(None, description="按标题ID筛选"),
    platform: Optional[int] = Query(None, description="平台筛选：1=小红书，2=抖音，3=快手，4=微信公众号"),
    publish_status: Optional[int] = Query(None, description="状态筛选：0=待发布，1=发布中，2=成功，3=失败，4=已删除"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: int = Depends(get_current_user_id)
):
    """
    获取发布记录列表
    """
    # 构建查询条件
    q_filter = {"user_id": user_id}
    if title_id is not None:
        q_filter["title_id"] = title_id
    if platform is not None:
        q_filter["platform"] = platform
    if publish_status is not None:
        q_filter["publish_status"] = publish_status

    # 查询总数
    total = await PublishRecord.filter(**q_filter).count()

    # 分页查询
    records = await PublishRecord.filter(**q_filter)\
        .order_by("-created_at")\
        .offset((page - 1) * page_size)\
        .limit(page_size)

    # 组装数据
    platform_map = {1: "小红书", 2: "抖音", 3: "快手", 4: "微信公众号"}
    status_map = {0: "待发布", 1: "发布中", 2: "成功", 3: "失败", 4: "已删除"}

    result = []
    for record in records:
        title = await Title.get_or_none(id=record.title_id)
        result.append({
            "id": record.id,
            "title_id": record.title_id,
            "title_name": title.title if title else None,
            "platform": record.platform,
            "platform_name": platform_map.get(record.platform, "未知"),
            "publish_status": record.publish_status,
            "status_name": status_map.get(record.publish_status, "未知"),
            "content": record.content,
            "publish_time": record.publish_time.strftime("%Y-%m-%d %H:%M:%S") if record.publish_time else None,
            "view_count": record.view_count,
            "like_count": record.like_count,
            "comment_count": record.comment_count,
            "share_count": record.share_count,
            "created_at": record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": record.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return {
        "code": 200,
        "message": "查询成功",
        "data": {
            "list": result,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.put("/{record_id}")
async def update_publish_record(
    record_id: int,
    body: UpdatePublishRecordRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    更新发布记录
    """
    record = await PublishRecord.get_or_none(id=record_id, user_id=user_id)
    if not record:
        return {"code": 404, "message": "发布记录不存在或无权限修改", "data": None}

    # 更新字段
    update_data = {}
    if body.publish_status is not None:
        update_data["publish_status"] = body.publish_status
        if body.publish_status == 2:
            update_data["publish_time"] = datetime.now()
    if body.content is not None:
        update_data["content"] = body.content
    if body.view_count is not None:
        update_data["view_count"] = body.view_count
    if body.like_count is not None:
        update_data["like_count"] = body.like_count
    if body.comment_count is not None:
        update_data["comment_count"] = body.comment_count
    if body.share_count is not None:
        update_data["share_count"] = body.share_count

    if update_data:
        for key, value in update_data.items():
            setattr(record, key, value)
        await record.save()

    return {
        "code": 200,
        "message": "更新成功",
        "data": {"id": record.id}
    }