"""
鍘嗗彶璁板綍妯″潡 - 鏌ヨ宸插彂甯冨唴瀹广€佸浘鐗囥€佸悓姝ョ瑪璁版暟鎹?
"""
import json

from fastapi import APIRouter, Depends, Query
from app.models import PublishRecord, PublishImage
from app.routers.auth import get_current_user_id
from app.agent.deepseek_agent import fetch_xhs_note

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/list")
async def list_publish_records(
    user_id: int = Depends(get_current_user_id),
):
    """鏍规嵁鐢ㄦ埛 ID 鏌ヨ鍙戝竷鐨勮褰?""
    records = await PublishRecord.filter(user_id=user_id).order_by("-id")

    return {
        "code": 200,
        "message": "鎴愬姛",
        "data": {
            "records": [
                {
                    "id": record.id,
                    "title_id": record.title_id,
                    "title": record.title_title,
                    "user_name": record.xhs_name,
                    "platform": record.platform,
                    "publish_status": record.publish_status,
                    "publish_time": record.publish_time.strftime("%Y-%m-%d %H:%M:%S") if record.publish_time else None,
                    "content": record.content,
                    "view_count": record.view_count,
                    "like_count": record.like_count,
                    "comment_count": record.comment_count,
                    "share_count": record.share_count,
                    "collected_count": record.collected_count,
                    "complete_url": record.complete_url,
                    "created_at": record.created_at.strftime("%Y-%m-%d %H:%M:%S") if record.created_at else None,
                    "updated_at": record.updated_at.strftime("%Y-%m-%d %H:%M:%S") if record.updated_at else None,
                }
                for record in records
            ]
        },
    }


@router.get("/get_publish_images")
async def get_publish_images_by_publish_id(
    publish_id: int = Query(...),
    user_id: int = Depends(get_current_user_id),
):
    """鏍规嵁鍙戝竷璁板綍 ID 鏌ヨ鍏宠仈鍥剧墖"""
    if not publish_id:
        return {"code": 400, "message": "鍙傛暟閿欒锛歱ublish_id 涓嶈兘涓虹┖", "data": None}

    images = await PublishImage.filter(publish_id=publish_id).order_by("sort_order")

    return {
        "code": 200,
        "message": "鎴愬姛",
        "data": {
            "images": [
                {
                    "id": img.id,
                    "publish_id": img.publish_id,
                    "image_id": img.image_id,
                    "image_url": img.image_url,
                    "image_type": img.image_type,
                    "sort_order": img.sort_order,
                }
                for img in images
            ]
        },
    }


@router.put("/update_complete_url")
async def update_complete_url(
    record_id: int = Query(...),
    complete_url: str = Query(...),
    user_id: int = Depends(get_current_user_id),
):
    """缁存姢绗旇鐨勫畬鏁?URL锛堝惈 xsec_token 绛夊弬鏁帮級"""
    record = await PublishRecord.filter(id=record_id, user_id=user_id).first()
    if not record:
        return {"code": 404, "message": "璁板綍涓嶅瓨鍦?, "data": None}

    record.complete_url = complete_url
    await record.save()

    return {"code": 200, "message": "淇敼鎴愬姛", "data": {"id": record.id, "complete_url": record.complete_url}}


@router.post("/sync_note_data")
async def sync_note_data(
    record_id: int = Query(...),
    user_id: int = Depends(get_current_user_id),
):
    """鏍规嵁绗旇 ID 鑾峰彇灏忕孩涔︿簰鍔ㄦ暟鎹苟鍥炲啓"""
    record = await PublishRecord.filter(id=record_id, user_id=user_id).first()
    if not record:
        return {"code": 404, "message": "璁板綍涓嶅瓨鍦?, "data": None}
    if not record.complete_url:
        return {"code": 400, "message": "璁板綍娌℃湁瀹屾暣 URL锛屾棤娉曡幏鍙栨暟鎹?, "data": None}

    try:
        result = fetch_xhs_note(record.complete_url)
        data = json.loads(result) if isinstance(result, str) else {}

        record.like_count = data.get("likedCount", 0)
        record.comment_count = data.get("commentCount", 0)
        record.share_count = data.get("shareCount", 0)
        record.collected_count = data.get("collectedCount", 0)
        await record.save()

        return {
            "code": 200,
            "message": "鍚屾鎴愬姛",
            "data": {
                "id": record.id,
                "like_count": record.like_count,
                "comment_count": record.comment_count,
                "share_count": record.share_count,
                "collected_count": record.collected_count,
            },
        }
    except json.JSONDecodeError:
        return {"code": 500, "message": "鏁版嵁瑙ｆ瀽澶辫触", "data": None}
    except Exception as e:
        return {"code": 500, "message": f"鍚屾澶辫触锛歿str(e)}", "data": None}
