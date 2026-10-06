"""
素材库模块 - 管理文案素材和图片素材
"""
import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, Body, Depends, File, Path as PathParam, UploadFile
from pydantic import BaseModel

from app.models import MaterialText, MaterialImage, Section, Title
from app.routers.auth import get_current_user_id
from app.util.upload import upload_image, upload_image_from_url

router = APIRouter(prefix="/material", tags=["material"])


class SaveTextBody(BaseModel):
    title: str
    content: str


class UploadImageByUrlBody(BaseModel):
    image_url: str


@router.get("/copies")
async def list_text_materials(
    user_id: int = Depends(get_current_user_id),
):
    """查询登录用户的文案素材列表"""
    texts = await MaterialText.filter(user_id=user_id).order_by("-id")
    return {
        "code": 200,
        "message": "查询成功",
        "data": {
            "list": [
                {
                    "id": t.id,
                    "title": t.title,
                    "content": t.content,
                    "created_at": t.created_at.strftime("%Y-%m-%d %H:%M:%S") if t.created_at else None,
                }
                for t in texts
            ]
        },
    }


@router.post("/copy")
async def create_text_material(
    body: SaveTextBody,
    user_id: int = Depends(get_current_user_id),
):
    """新增文案素材"""
    text = await MaterialText.create(
        user_id=user_id,
        title=body.title or "",
        content=body.content or "",
    )
    return {
        "code": 200,
        "message": "新增成功",
        "data": {
            "id": text.id,
            "title": text.title,
            "content": text.content,
            "created_at": text.created_at.strftime("%Y-%m-%d %H:%M:%S") if text.created_at else None,
        },
    }


@router.put("/copy/{copy_id}")
async def update_text_material(
    copy_id: int = PathParam(..., description="文案素材 ID"),
    body: SaveTextBody = Body(...),
    user_id: int = Depends(get_current_user_id),
):
    """修改文案素材"""
    text = await MaterialText.filter(id=copy_id, user_id=user_id).first()
    if not text:
        return {"code": 404, "message": "文案素材不存在或无权限", "data": None}
    if body.title is not None:
        text.title = body.title
    if body.content is not None:
        text.content = body.content
    await text.save()

    return {
        "code": 200,
        "message": "修改成功",
        "data": {
            "id": text.id,
            "title": text.title,
            "content": text.content,
            "created_at": text.created_at.strftime("%Y-%m-%d %H:%M:%S") if text.created_at else None,
        },
    }


@router.delete("/copy/{copy_id}")
async def delete_text_material(
    copy_id: int = PathParam(..., description="文案素材 ID"),
    user_id: int = Depends(get_current_user_id),
):
    """删除文案素材"""
    text = await MaterialText.filter(id=copy_id, user_id=user_id).first()
    if not text:
        return {"code": 404, "message": "文案素材不存在或无权限", "data": None}
    await text.delete()
    return {"code": 200, "message": "删除成功", "data": None}


@router.post("/copy/{copy_id}/use")
async def use_text_material(
    copy_id: int = PathParam(..., description="文案素材 ID"),
    user_id: int = Depends(get_current_user_id),
):
    """从素材库创建草稿标题，返回 title_id"""
    text = await MaterialText.filter(id=copy_id, user_id=user_id).first()
    if not text:
        return {"code": 404, "message": "文案素材不存在", "data": None}
    section = await Section.create(user_id=user_id, source_name="素材库复用", name="素材库")
    title = await Title.create(section_id=section.id, title=text.title or "素材复用", sort_order=1, content=text.content or "", status="1")
    return {"code": 200, "message": "ok", "data": {"title_id": title.id, "title": title.title, "content": title.content}}


@router.get("/images")
async def list_image_materials(
    user_id: int = Depends(get_current_user_id),
):
    """查询登录用户的图片素材列表"""
    images = await MaterialImage.filter(user_id=user_id).order_by("-id")
    return {
        "code": 200,
        "message": "查询成功",
        "data": {
            "list": [
                {
                    "id": img.id,
                    "image_url": img.image_url or "",
                    "created_at": img.created_at.strftime("%Y-%m-%d %H:%M:%S") if img.created_at else None,
                }
                for img in images
            ]
        },
    }


@router.post("/image/upload")
async def upload_image_material(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
):
    """上传素材图片到 OSS"""
    if not file.content_type or not file.content_type.startswith("image/"):
        return {"code": 400, "message": "请上传图片文件", "data": None}

    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name
        content = await file.read()
        tmp.write(content)

    try:
        upload_result = upload_image(tmp_path)
        oss_url = upload_result["url"]
    except Exception as e:
        return {"code": 500, "message": f"上传失败: {e}", "data": None}
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    image = await MaterialImage.create(
        user_id=user_id,
        image_url=oss_url,
    )

    return {
        "code": 200,
        "message": "成功",
        "data": {
            "id": image.id,
            "image_url": image.image_url,
            "created_at": image.created_at.strftime("%Y-%m-%d %H:%M:%S") if image.created_at else None,
        },
    }


@router.post("/image/upload-url")
async def upload_image_material_by_url(
    body: UploadImageByUrlBody,
    user_id: int = Depends(get_current_user_id),
):
    """通过网络 URL 上传素材图片到 OSS"""
    try:
        upload_result = upload_image_from_url(image_url=body.image_url)
        oss_url = upload_result["url"]
    except Exception as e:
        return {"code": 500, "message": f"上传失败: {e}", "data": None}

    image = await MaterialImage.create(
        user_id=user_id,
        image_url=oss_url,
    )

    return {
        "code": 200,
        "message": "成功",
        "data": {
            "id": image.id,
            "image_url": image.image_url,
            "created_at": image.created_at.strftime("%Y-%m-%d %H:%M:%S") if image.created_at else None,
        },
    }


@router.delete("/image/{image_id}")
async def delete_image_material(
    image_id: int = PathParam(..., description="素材图片 ID"),
    user_id: int = Depends(get_current_user_id),
):
    """删除素材图片"""
    image = await MaterialImage.filter(id=image_id, user_id=user_id).first()
    if not image:
        return {"code": 404, "message": "素材图片不存在或无权限", "data": None}
    await image.delete()
    return {"code": 200, "message": "删除成功", "data": None}
