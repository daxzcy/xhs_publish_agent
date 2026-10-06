"""
发布图片关联模块 - 管理发布内容与图片的关联
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.models import PublishImage, PublishRecord, TitleImage
from app.routers.auth import get_current_user_id

router = APIRouter(prefix="/publish_images", tags=["publish_images"])


class CreatePublishImagesRequest(BaseModel):
    publish_id: int
    image_ids: List[int]  # t_title_images 表的 ID 列表


class PublishImageResponse(BaseModel):
    id: int
    publish_id: int
    image_id: int
    image_type: int
    sort_order: int
    image_url: Optional[str] = None
    created_at: str


@router.get("/get_publish_images")
async def get_publish_images(
    publish_id: int = Query(..., description="发布记录ID"),
    user_id: int = Depends(get_current_user_id)
):
    """
    获取某个发布记录关联的所有图片
    """
    # 验证发布记录是否存在
    record = await PublishRecord.get_or_none(id=publish_id)
    if not record:
        return {"code": 404, "message": "发布记录不存在", "data": None}

    # 查询关联图片
    publish_images = await PublishImage.filter(publish_id=publish_id)\
        .order_by("sort_order", "id")

    # 获取图片详情
    result = []
    for pi in publish_images:
        title_image = await TitleImage.get_or_none(id=pi.image_id)
        result.append({
            "id": pi.id,
            "publish_id": pi.publish_id,
            "image_id": pi.image_id,
            "image_type": pi.image_type,
            "image_type_name": ["", "正文图", "封面图", "详情图"][pi.image_type] if 1 <= pi.image_type <= 3 else "未知",
            "sort_order": pi.sort_order,
            "image_url": title_image.image_url if title_image else None,
            "created_at": pi.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return {
        "code": 200,
        "message": "查询成功",
        "data": {
            "publish_id": publish_id,
            "images": result,
            "count": len(result)
        }
    }


@router.post("/create_publish_images")
async def create_publish_images(
    body: CreatePublishImagesRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    保存发布图片关联
    """
    # 验证发布记录是否存在
    record = await PublishRecord.get_or_none(id=body.publish_id, user_id=user_id)
    if not record:
        return {"code": 404, "message": "发布记录不存在或无权限操作", "data": None}

    if not body.image_ids:
        return {"code": 400, "message": "请至少选择一张图片", "data": None}

    # 验证所有图片是否存在
    valid_images = await TitleImage.filter(id__in=body.image_ids, user_id=user_id)
    valid_ids = {img.id for img in valid_images}
    invalid_ids = [img_id for img_id in body.image_ids if img_id not in valid_ids]

    if invalid_ids:
        return {
            "code": 400,
            "message": f"以下图片不存在或无权限: {invalid_ids}",
            "data": None
        }

    # 删除已存在的关联（如果有）
    await PublishImage.filter(publish_id=body.publish_id).delete()

    # 创建新的关联
    created = []
    for idx, image_id in enumerate(body.image_ids):
        # 获取图片信息以确定类型
        title_image = await TitleImage.get(id=image_id)
        publish_image = await PublishImage.create(
            publish_id=body.publish_id,
            image_id=image_id,
            image_type=title_image.image_type + 1,  # 0->1, 1->2, 2->3
            sort_order=idx + 1,
            created_at=datetime.now()
        )
        created.append({
            "id": publish_image.id,
            "publish_id": publish_image.publish_id,
            "image_id": publish_image.image_id,
            "image_type": publish_image.image_type,
            "sort_order": publish_image.sort_order
        })

    return {
        "code": 200,
        "message": "保存成功",
        "data": {
            "publish_id": body.publish_id,
            "images": created,
            "count": len(created)
        }
    }


@router.delete("/{publish_image_id}")
async def delete_publish_image(
    publish_image_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """
    删除发布图片关联
    """
    # 验证关联是否存在且属于当前用户的发布记录
    publish_image = await PublishImage.get_or_none(id=publish_image_id)
    if not publish_image:
        return {"code": 404, "message": "关联不存在", "data": None}

    record = await PublishRecord.get_or_none(id=publish_image.publish_id, user_id=user_id)
    if not record:
        return {"code": 403, "message": "无权限操作", "data": None}

    await publish_image.delete()

    return {
        "code": 200,
        "message": "删除成功",
        "data": {"id": publish_image_id}
    }