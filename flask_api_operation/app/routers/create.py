# 鐢熸垚杩愯惀鍐呭鎵€鐢ㄧ殑API
import asyncio
import functools
import json
import logging
import os
import re
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, File, Path as PathParam, Query, UploadFile
from pydantic import BaseModel

from app.agent.deepseek_agent import hot_topic, content_creation
from app.agent.qwen_agent import generate_cover_prompt, generate_image
from app.models import AIModel, MaterialImage, MaterialText, PublishImage, PublishRecord, Section, Style, Title, TitleImage, XhsAccount
from app.routers.auth import get_current_user_id
from app.util.upload import upload_image, upload_image_from_url
from app.util.xhs_publish import publish_xhs_note

logger = logging.getLogger(__name__)

# 鍒涘缓璺敱瀹炰緥
router = APIRouter(prefix="/create", tags=["create"])

# 瀹氫箟璇锋眰妯″瀷锛堟牴鎹富棰樼敓鎴愰鐩級
class CreateByThemeBody(BaseModel):
    theme: str

# 澶勭悊Agent杩斿洖鐨勬枃鏈紝鎻愬彇鍏朵腑鐨凧SON
def _extract_json(text: str) -> dict:
    text = (text or "").strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    return json.loads(text)

# 鏍规嵁涓婚璋冪敤Agent鐢熸垚鏉垮潡锛屾爣棰橈紝瑙ｆ瀽鍚庡啓鍏ユ暟鎹簱骞惰繑鍥?
@router.post("/start")
async def create_by_theme(
    body: CreateByThemeBody, 
    user_id: int = Depends(get_current_user_id)
):
    # 楠岃瘉杈撳叆鐨勪富棰樻槸鍚︿负绌?
    theme = (body.theme or "").strip()
    if not theme:
        return {"code": 400, "message": "璇疯緭鍏ヤ富棰?,"data": None}

    # 璋冪敤Coze鐢熸垚鏉垮潡涓庢爣棰?
    try:
        raw = hot_topic(theme)
    except Exception as e:
        return {"code": 500, "message": f"璋冪敤 agent 澶辫触: {e}", "data": None}

    # 瑙ｆ瀽Coze杩斿洖鐨凧SON
    try:
        data = _extract_json(raw)
    except Exception as e:
        return {"code": 500, "message": f"瑙ｆ瀽agent杩斿洖缁撴灉澶辫触: {e}", "data": None}

    # 楠岃瘉杩斿洖鏍煎紡鏄惁姝ｇ‘
    if not isinstance(data, dict):
        return {"code": 500, "message": "agent杩斿洖鏍煎紡寮傚父", "data": None}

    # 瀛樺偍鏉垮潡鏁版嵁
    sections_out = []
    # 閬嶅巻杩斿洖鐨勬澘鍧椾笌鏍囬
    for section_name,title_list in data.items():
        # 楠岃瘉鏉垮潡鍚嶇О鍜屾爣棰樺垪琛ㄦ槸鍚︿负绌?
        if not section_name or not isinstance(title_list, list):
            continue

        # 灏嗘澘鍧楁暟鎹啓鍏ユ暟鎹簱
        section = await Section.create(
            user_id=user_id,
            source_name= theme if theme else None,
            name = section_name,
            created_at = datetime.now()
        )

        # 瀛樺偍鏍囬鏁版嵁
        title_out = []
        # 閬嶅巻鏍囬鍒楄〃鍜屾帓搴忓簭鍙?
        for sort_order,title_text in enumerate(title_list,start=1):
            # 楠岃瘉鏍囬鏄惁涓哄瓧绗︿覆
            if not isinstance(title_text, str):
                title_text = str(title_text)
            
            # 灏嗘爣棰樻暟鎹啓鍏ユ暟鎹簱
            title_row = await Title.create(
                section_id = section.id,
                title = title_text,
                sort_order = sort_order,
                created_at = datetime.now()
            )
            # 瀛樺偍鏍囬鏁版嵁
            title_out.append({
                "id": title_row.id,
                "title": title_row.title,
                "content": title_row.content,
                "status": title_row.status,
                "sort_order": title_row.sort_order,
                "created_at": title_row.created_at
            })
        
        # 瀛樺偍鏉垮潡鏁版嵁
        sections_out.append({
            "id": section.id,
            "name": section.name,
            "created_at": section.created_at,
            "titles": title_out
        })
    # 杩斿洖缁撴灉
    return {"code": 200, "message": "鎴愬姛", "data": {"sections": sections_out}}


# 妫€绱㈠綋鍓嶇敤鎴峰凡鏈変富棰樺垪琛紝鍙€夊叧閿瘝杩囨护
@router.get("/themes")
async def list_themes(
    keyword: str | None= Query(None),
    user_id: int = Depends(get_current_user_id)
):
    # 浠庢暟鎹簱涓煡鎵捐鐢ㄦ埛鐨勬墍鏈夌敓鎴愯繃鐨勬澘鍧楁暟鎹?
    sections = await Section.filter(user_id=user_id).values_list("source_name",flat=True);
    # 鍘婚噸锛屽緱鍒颁富棰樻暟鎹?
    themes = list(set(sections))

    # 濡傛灉鏈塳eyword鍙傛暟锛岃繘琛屽叧閿瘝杩囨护
    if keyword:
        kw = (keyword or "").lower()
        themes = [t for t in themes if kw in t.lower()]
    # 瀵逛富棰樺垪琛ㄨ繘琛屾帓搴?
    themes.sort()

    # 杩斿洖鏁版嵁
    return {"code": 200, "message": "鎴愬姛", "data": {"themes": themes}}


# 鎸変富棰樺悕浠庢暟鎹簱鍔犺浇宸茬粡鐢熸垚鐨勬爣棰橈紝杩斿洖鏍煎紡涓?/start 涓€鑷达紝渚夸簬鍓嶇澶嶇敤
@router.get("/load")
async def load_by_theme(
    theme: str = Query(...), # 蹇呭～
    user_id: int = Depends(get_current_user_id)
):
    # 楠岃瘉涓婚鏄惁涓虹┖
    if not theme:
        return {"code": 400, "message": "涓婚涓嶈兘涓虹┖","data": None}

    # 鏍规嵁鐢ㄦ埛 + 涓婚鏌ヨ鏉垮潡
    sections = await Section.filter(user_id=user_id, source_name=theme).order_by("id")

    # 鎻愬彇鏉垮潡鐨処D鍒楄〃
    section_ids = [section.id for section in sections]

    # 鏍规嵁鏉垮潡ID鏌ヨ鏍囬
    titles = await Title.filter(section_id__in=section_ids).order_by("section_id", "sort_order")

    # 灏佽鎴愪竴涓垪琛?
    # 鍒涘缓涓€涓瓧鍏革紝key鏄澘鍧梚d锛寁alue鏄鏉垮潡涓嬬殑鏍囬鍒楄〃
    titles_by_sec = {}
    # 閬嶅巻鏍囬鍒楄〃锛屽皢鏍囬鎸夌収鏉垮潡id鍒嗙粍
    for title in titles:
        titles_by_sec.setdefault(title.section_id, []).append(title)
    
    # 鍒涘缓涓€涓垪琛紝鐢ㄤ簬瀛樺偍鏉垮潡鏁版嵁
    sections_out = []
    # 閬嶅巻鏉垮潡鍒楄〃锛屽皢鏉垮潡鏁版嵁鍜屾爣棰樻暟鎹粍瑁呮垚涓€涓瓧鍏?
    for section in sections:
        titles_out = [
            {
                "id": title.id,
                "title": title.title,
                "content": title.content,
                "status": title.status,
                "sort_order": title.sort_order,
                "created_at": title.created_at
            }
            # 鑾峰彇璇ユ澘鍧椾笅鐨勬墍鏈夋爣棰?
            for title in titles_by_sec.get(section.id, [])
        ]
        sections_out.append({
            "id": section.id,
            "name": section.name,
            "created_at": section.created_at,
            "titles": titles_out
        })

    # 杩斿洖鏁版嵁
    return {
        "code": 200, 
        "message": "鎴愬姛", 
        "data": {"sections": sections_out}
    }

# 璇锋眰浣擄紝鏍规嵁鏍囬鐢熸垚鍐呭
class CreateCopyBody(BaseModel):
    title_text: str              # 鏍囬鏂囨湰
    title_id: int | None = None  # 鏍囬ID

# 鏍规嵁閫変腑鐨勬爣棰橈紝璋冪敤鍐呭鍒涗綔Agent锛岃繑鍥炵敓鎴愮殑鏂囨
@router.post("/copy")
async def create_copy(
    body: CreateCopyBody,
    user_id: int = Depends(get_current_user_id)
):
    # 楠岃瘉鏍囬鏂囨湰鏄惁涓虹┖
    title_text = (body.title_text or "").strip()
    if not title_text:
        return {"code": 400, "message": "璇蜂紶鍏ユ爣棰?,"data": None}

    # 璋冪敤Coze鏅鸿兘浣撶敓鎴愭枃妗?
    try:
        content = content_creation(title_text)
    except Exception as e:
        return {"code": 500, "message": f"璋冪敤 agent 澶辫触: {e}", "data": None}

    # 濡傛灉浼犲叆浜嗘爣棰榠d锛屽皢鏂囨鍐欏叆璇ユ爣棰樼殑content瀛楁锛屽苟灏嗙姸鎬佹洿鏂颁负1锛堝凡鐢熸垚锛?
    if body.title_id:
        title = await Title.get(id=body.title_id).first()
        if title:
            title.content = content if content else None
            title.status = "1"
            await title.save()

    # 杩斿洖缁撴灉
    return {
        "code": 200, 
        "message": "鎴愬姛", 
        "data": {"content": content}
    }

# 鏌ユ壘鏁版嵁搴撲腑鐨勬爣棰樿鎯?
@router.get("/title/{title_id}")
async def get_title_detail(
    # 鏍囬ID锛屽繀濉?
    title_id: int = PathParam(...,description="鏍囬ID"),
    user_id: int = Depends(get_current_user_id)
):
    # 鏍规嵁鏍囬ID鏌ヨ鏍囬
    title = await Title.get(id=title_id).first()

    # 濡傛灉鏍囬涓嶅瓨鍦紝杩斿洖閿欒淇℃伅
    if not title:
        return {"code": 400, "message": "鏍囬涓嶅瓨鍦?,"data": None}

    # 鏍规嵁鏍囬ID鏌ヨ鏉垮潡
    section = await Section.get(id=title.section_id).first()

    # 濡傛灉鏉垮潡涓嶅瓨鍦ㄦ垨鑰呮澘鍧椾笉灞炰簬褰撳墠鐧诲綍鐢ㄦ埛锛岃繑鍥為敊璇俊鎭?
    if not section or section.user_id != user_id:
        return {"code": 403, "message": "鏃犳潈璁块棶璇ユ爣棰?,"data": None}

    # 杩斿洖鏍囬璇︽儏
    return {
        "code": 200,
        "message": "鎴愬姛",
        "data": {
            "id": title.id,
            "title": title.title,
            "content": title.content,
            "status": title.status,
            "view_count": title.view_count,
            "like_count": title.like_count,
        }
    }


# 璇锋眰浣擄紝淇濆瓨鏂囨
class SaveCopyBody(BaseModel):
    content: str = ""

# 淇濆瓨鏂囨锛岀敤浜庢枃妗堢紪瀵兼楠わ紝缂栬緫鏂囨鍚庝繚瀛樺埌鏁版嵁搴?
@router.post("/save-copy")
async def save_copy(
    title_id: int = Query(...,description="鏍囬ID"),
    body: SaveCopyBody = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    # 鏍规嵁鏍囬ID鏌ヨ鏍囬
    title = await Title.get(id=title_id).first()

    # 濡傛灉鏍囬涓嶅瓨鍦紝杩斿洖閿欒淇℃伅
    if not title:
        return {"code": 400, "message": "鏍囬涓嶅瓨鍦?,"data": None}

    # 鏍规嵁鏍囬ID鏌ヨ鏉垮潡
    section = await Section.get(id=title.section_id).first()

    # 濡傛灉鏉垮潡涓嶅瓨鍦ㄦ垨鑰呮澘鍧椾笉灞炰簬褰撳墠鐧诲綍鐢ㄦ埛锛岃繑鍥為敊璇俊鎭?
    if not section or section.user_id != user_id:
        return {"code": 403, "message": "鏃犳潈璁块棶璇ユ爣棰?,"data": None}
    
    # 鏇存柊鏍囬鐨勬枃妗?
    title.content = body.content if body.content else None
    await title.save()

    # 杩斿洖缁撴灉
    return {
        "code": 200,
        "message": "鎴愬姛",
        "data": {"id": title.id}
    }

# 鑾峰彇椋庢牸鍒楄〃
@router.get("/styles")
async def get_style_list(
    user_id: int = Depends(get_current_user_id)
):
    # 浠庢暟鎹簱涓墍鏈夐鏍?
    styles = await Style.all().order_by("id")
    list_out = [
        {
            "id": style.id,
            "name": style.name or "",
            "fengge": style.fengge or "",
            "create_time": style.create_time.strftime("%Y-%m-%d %H:%M:%S") if style.create_time else None
        }
        for style in styles
    ]
    # 杩斿洖椋庢牸鍒楄〃
    return {"code": 200, "message": "鎴愬姛", "data": {"styles": list_out}}


class GenerateCoverBody(BaseModel):
    """AI 鐢熸垚灏侀潰璇锋眰浣?""
    title_id: int
    prompt: str                     # 椋庢牸鎻愮ず璇?


class SaveCoverImageBody(BaseModel):
    """浠庣礌鏉愬簱淇濆瓨灏侀潰鍥?""
    title_id: int
    image_url: str


class SaveMaterialImageBody(BaseModel):
    """浠庣礌鏉愬簱淇濆瓨姝ｆ枃鍥?""
    title_id: int
    image_url: str


class UploadImageByUrlBody(BaseModel):
    """閫氳繃缃戠粶 URL 涓婁紶鍥剧墖"""
    title_id: int
    image_url: str
    image_type: int = 0  # 0=姝ｆ枃鍥? 1=灏侀潰鍥?


class UpdateTitleBody(BaseModel):
    """淇敼鏍囬涓庢枃妗?""
    title: str = ""
    content: str = ""


class PublishBody(BaseModel):
    """鍙戝竷绗旇璇锋眰浣?""
    title_id: int                    # 鏍囬 ID
    account_ids: List[int]           # 閫変腑鐨勫皬绾功璐﹀彿 ID 鍒楄〃


# 绾跨▼姹狅紝鐢ㄤ簬鎵ц Playwright 鍚屾浠ｇ爜
playwright_pool = ThreadPoolExecutor(max_workers=3)

@router.get("/models")
async def get_models(
    model_type: Optional[str] = Query(None, description="妯″瀷绫诲瀷锛歵ext=鏂囨湰鐢熸垚锛宨mage=鍥惧儚鐢熸垚"),
    user_id: int = Depends(get_current_user_id)
):
    """
    鑾峰彇 AI 妯″瀷鍒楄〃
    """
    qs = AIModel.filter(status=1)
    if model_type:
        qs = qs.filter(type=model_type)
    models = await qs.order_by("id")

    result = [{
        "id": m.id,
        "name": m.name,
        "type": m.type,
        "version": m.version,
        "description": m.description,
        "status": m.status,
        "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None
    } for m in models]

    return {
        "code": 200,
        "message": "鏌ヨ鎴愬姛",
        "data": {"models": result}
    }


@router.post("/cover")
async def generate_cover(
    body: GenerateCoverBody,
    user_id: int = Depends(get_current_user_id)
):
    """
    璋冪敤 AI 鐢熸垚灏侀潰鍥?鈫?涓婁紶 OSS 鈫?鍐欏叆 t_title_images
    """
    # 楠岃瘉椋庢牸鎻愮ず璇?
    prompt = (body.prompt or "").strip()
    if not prompt:
        return {"code": 400, "message": "璇蜂紶鍏ラ鏍兼彁绀鸿瘝", "data": None}

    # 楠岃瘉鏍囬鏄惁瀛樺湪
    title = await Title.get_or_none(id=body.title_id)
    if not title:
        return {"code": 404, "message": "鏍囬涓嶅瓨鍦?, "data": None}

    # 楠岃瘉鏍囬鎵€灞炴澘鍧楁槸鍚﹀睘浜庡綋鍓嶇敤鎴?
    section = await Section.get_or_none(id=title.section_id)
    if not section or section.user_id != user_id:
        return {"code": 403, "message": "鏃犳潈鎿嶄綔璇ユ爣棰?, "data": None}

    # 1. 鏋勫缓鎻愮ず璇嶅苟鐢熸垚鍥剧墖
    try:
        full_prompt = generate_cover_prompt(
            title=title.title,
            style_description=prompt,
            include_text=True,
        )
        image_url = generate_image(prompt=full_prompt)
    except Exception as e:
        return {"code": 500, "message": f"鐢熸垚灏侀潰鍥惧け璐? {e}", "data": None}

    if not image_url:
        return {"code": 500, "message": "鍥剧墖鐢熸垚鏈繑鍥炵粨鏋?, "data": None}

    # 2. 涓婁紶鍒?OSS
    try:
        upload_result = upload_image_from_url(image_url=image_url)
        oss_url = upload_result["url"]
    except Exception as e:
        return {"code": 500, "message": f"涓婁紶灏侀潰鍥惧け璐? {e}", "data": None}

    # 3. 鍐欏叆鏁版嵁搴擄紙宸叉湁鍒欐浛鎹紝鏃犲垯鏂板缓锛?
    existing = await TitleImage.filter(title_id=body.title_id, image_type=1).first()
    if existing:
        existing.image_url = oss_url
        existing.created_at = datetime.now()
        await existing.save()
        image_id = existing.id
    else:
        created = await TitleImage.create(
            user_id=user_id,
            title_id=body.title_id,
            image_url=oss_url,
            image_type=1,        # 灏侀潰鍥?
            sort_order=0,
        )
        image_id = created.id

    return {
        "code": 200,
        "message": "鎴愬姛",
        "data": {"image_url": oss_url, "image_id": image_id},
    }


# ---------- 灏侀潰鍥炬煡璇?/ 涓婁紶 ----------

@router.get("/covers/{title_id}")
async def get_title_cover(
    title_id: int = PathParam(..., description="鏍囬 ID"),
    user_id: int = Depends(get_current_user_id),
):
    """鑾峰彇鏍囬鐨勫皝闈㈠浘"""
    title = await Title.get_or_none(id=title_id)
    if not title:
        return {"code": 404, "message": "鏍囬涓嶅瓨鍦?, "data": None}

    cover = await TitleImage.filter(title_id=title_id, image_type=1).first()
    return {"code": 200, "message": "鎴愬姛", "data": {"covers": cover}}


@router.post("/cover/upload")
async def upload_cover_image(
    file: UploadFile = File(...),
    title_id: int = Query(...),
    user_id: int = Depends(get_current_user_id),
):
    """涓婁紶灏侀潰鍥撅紙鎺ユ敹鍓嶇鏂囦欢锛夆啋 OSS 鈫?鍐欏叆鏁版嵁搴?""
    if not file.content_type or not file.content_type.startswith("image/"):
        return {"code": 400, "message": "璇蜂笂浼犲浘鐗囨枃浠?, "data": None}

    # 鍐欏叆涓存椂鏂囦欢
    # 1.鑾峰彇suffix鍚庣紑
    suffix = Path(file.filename).suffix
    # 2.鍒涘缓涓存椂鏂囦欢锛屽苟鑾峰彇涓存椂鏂囦欢璺緞锛屾渶鍚庡啓鍏ユ枃浠?
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name
        # content = await file.read()
        # tmp.write(content)
        for chunk in file.iter_content(chunk_size=8192):
            tmp.write(chunk)

    try:
        upload_result = upload_image(tmp_path)
        oss_url = upload_result["url"]
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    # 宸叉湁灏侀潰鍒欐浛鎹紝鏃犲垯鏂板缓
    existing = await TitleImage.filter(title_id=title_id, image_type=1).first()
    if existing:
        existing.image_url = oss_url
        await existing.save()
        image_id = existing.id
    else:
        created = await TitleImage.create(
            user_id=user_id,
            title_id=title_id,
            image_url=oss_url,
            image_type=1,
            sort_order=0,
        )
        image_id = created.id

    return {"code": 200, "message": "涓婁紶鎴愬姛", "data": {"image_url": oss_url, "image_id": image_id}}


@router.post("/cover-image")
async def save_cover_image(
    body: SaveCoverImageBody,
    user_id: int = Depends(get_current_user_id),
):
    """浠庣礌鏉愬簱閫夋嫨鍥剧墖璁句负灏侀潰鍥?""
    title = await Title.get_or_none(id=body.title_id)
    if not title:
        return {"code": 404, "message": "鏍囬涓嶅瓨鍦?, "data": None}

    section = await Section.get_or_none(id=title.section_id)
    if not section or section.user_id != user_id:
        return {"code": 403, "message": "鏃犳潈鎿嶄綔璇ユ爣棰?, "data": None}

    existing = await TitleImage.filter(title_id=body.title_id, image_type=1).first()
    if existing:
        existing.image_url = body.image_url
        await existing.save()
        image_id = existing.id
    else:
        created = await TitleImage.create(
            user_id=user_id,
            title_id=body.title_id,
            image_url=body.image_url,
            image_type=1,
            sort_order=0,
        )
        image_id = created.id

    return {"code": 200, "message": "鎴愬姛", "data": {"image_url": body.image_url, "image_id": image_id}}


# ---------- 姝ｆ枃鍥句笂浼?/ 鏌ヨ / 鍒犻櫎 ----------

@router.post("/image/upload")
async def upload_content_image(
    file: UploadFile = File(...),
    title_id: int = Query(...),
    user_id: int = Depends(get_current_user_id),
):
    """涓婁紶姝ｆ枃鍥?鈫?OSS 鈫?鍐欏叆 t_title_images"""
    if not file.content_type or not file.content_type.startswith("image/"):
        return {"code": 400, "message": "璇蜂笂浼犲浘鐗囨枃浠?, "data": None}

    title = await Title.get_or_none(id=title_id)
    if not title:
        return {"code": 404, "message": "鏍囬涓嶅瓨鍦?, "data": None}

    section = await Section.get_or_none(id=title.section_id)
    if not section or section.user_id != user_id:
        return {"code": 403, "message": "鏃犳潈鎿嶄綔璇ユ爣棰?, "data": None}

    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name
        content = await file.read()
        tmp.write(content)

    try:
        upload_result = upload_image(tmp_path)
        oss_url = upload_result["url"]
    except Exception as e:
        return {"code": 500, "message": f"涓婁紶鍥剧墖澶辫触: {e}", "data": None}
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    # sort_order = 宸叉湁姝ｆ枃鍥炬渶澶?sort_order + 1
    max_order_row = await TitleImage.filter(
        title_id=title_id, image_type=0,
    ).order_by("-sort_order").first()
    next_order = (max_order_row.sort_order + 1) if max_order_row else 1

    created = await TitleImage.create(
        user_id=user_id,
        title_id=title_id,
        image_url=oss_url,
        image_type=0,            # 姝ｆ枃鍥?
        sort_order=next_order,
    )

    return {"code": 200, "message": "涓婁紶鎴愬姛", "data": {"image_url": oss_url, "image_id": created.id}}


@router.post("/image/upload-url")
async def upload_content_image_by_url(
    body: UploadImageByUrlBody,
    user_id: int = Depends(get_current_user_id),
):
    """閫氳繃缃戠粶 URL 涓婁紶鍥剧墖 鈫?OSS 鈫?鍐欏叆 t_title_images"""
    title = await Title.get_or_none(id=body.title_id)
    if not title:
        return {"code": 404, "message": "鏍囬涓嶅瓨鍦?, "data": None}

    section = await Section.get_or_none(id=title.section_id)
    if not section or section.user_id != user_id:
        return {"code": 403, "message": "鏃犳潈鎿嶄綔璇ユ爣棰?, "data": None}

    try:
        upload_result = upload_image_from_url(image_url=body.image_url)
        oss_url = upload_result["url"]
    except Exception as e:
        return {"code": 500, "message": f"涓婁紶鍥剧墖澶辫触: {e}", "data": None}

    if body.image_type == 1:
        # 灏侀潰鍥撅細宸叉湁鍒欐浛鎹紝鏃犲垯鏂板缓
        existing = await TitleImage.filter(title_id=body.title_id, image_type=1).first()
        if existing:
            existing.image_url = oss_url
            existing.created_at = datetime.now()
            await existing.save()
            return {"code": 200, "message": "涓婁紶鎴愬姛", "data": {"image_url": oss_url, "image_id": existing.id}}
        else:
            created = await TitleImage.create(
                user_id=user_id,
                title_id=body.title_id,
                image_url=oss_url,
                image_type=1,
                sort_order=0,
            )
            return {"code": 200, "message": "涓婁紶鎴愬姛", "data": {"image_url": oss_url, "image_id": created.id}}
    else:
        # 姝ｆ枃鍥撅細杩藉姞
        max_order_row = await TitleImage.filter(
            title_id=body.title_id, image_type=0,
        ).order_by("-sort_order").first()
        next_order = (max_order_row.sort_order + 1) if max_order_row else 1

        created = await TitleImage.create(
            user_id=user_id,
            title_id=body.title_id,
            image_url=oss_url,
            image_type=0,
            sort_order=next_order,
        )
        return {"code": 200, "message": "涓婁紶鎴愬姛", "data": {"image_url": oss_url, "image_id": created.id}}


@router.get("/images/{title_id}")
async def get_title_images(
    title_id: int = PathParam(..., description="鏍囬 ID"),
    user_id: int = Depends(get_current_user_id),
):
    """鑾峰彇鏍囬鐨勬鏂囧浘鍒楄〃"""
    images = await TitleImage.filter(title_id=title_id, image_type=0).order_by("sort_order")
    return {
        "code": 200,
        "message": "鎴愬姛",
        "data": {
            "images": [
                {"id": img.id, "image_url": img.image_url, "sort_order": img.sort_order}
                for img in images
            ]
        },
    }


@router.delete("/image/{image_id}")
async def delete_content_image(
    image_id: int = PathParam(..., description="鍥剧墖 ID"),
    user_id: int = Depends(get_current_user_id),
):
    """鍒犻櫎姝ｆ枃鍥?""
    image_row = await TitleImage.filter(id=image_id, user_id=user_id, image_type=0).first()
    if not image_row:
        return {"code": 404, "message": "鍥剧墖涓嶅瓨鍦ㄦ垨鏃犳潈闄?, "data": None}
    await image_row.delete()
    return {"code": 200, "message": "鍒犻櫎鎴愬姛", "data": None}


@router.post("/material-image")
async def save_material_image(
    body: SaveMaterialImageBody,
    user_id: int = Depends(get_current_user_id),
):
    """浠庣礌鏉愬簱閫夋嫨鍥剧墖杩藉姞涓烘鏂囧浘"""
    title = await Title.get_or_none(id=body.title_id)
    if not title:
        return {"code": 404, "message": "鏍囬涓嶅瓨鍦?, "data": None}

    section = await Section.get_or_none(id=title.section_id)
    if not section or section.user_id != user_id:
        return {"code": 403, "message": "鏃犳潈鎿嶄綔璇ユ爣棰?, "data": None}

    max_order_row = await TitleImage.filter(
        title_id=body.title_id, image_type=0,
    ).order_by("-sort_order").first()
    next_order = (max_order_row.sort_order + 1) if max_order_row else 1

    created = await TitleImage.create(
        user_id=user_id,
        title_id=body.title_id,
        image_url=body.image_url,
        image_type=0,
        sort_order=next_order,
    )

    return {"code": 200, "message": "鎴愬姛", "data": {"image_url": created.image_url, "image_id": created.id}}


# ---------- 淇敼鏍囬涓庢枃妗?----------

@router.put("/title/{title_id}")
async def update_title(
    title_id: int = PathParam(..., description="鏍囬 ID"),
    body: UpdateTitleBody = Body(...),
    user_id: int = Depends(get_current_user_id),
):
    """鍙戝竷鍓嶆渶鍚庝竴娆′慨鏀规爣棰樺拰鏂囨"""
    title = await Title.get_or_none(id=title_id)
    if not title:
        return {"code": 404, "message": "鏍囬涓嶅瓨鍦?, "data": None}

    section = await Section.get_or_none(id=title.section_id)
    if not section or section.user_id != user_id:
        return {"code": 403, "message": "鏃犳潈鎿嶄綔璇ユ爣棰?, "data": None}

    title.title = (body.title or "").strip() or title.title
    title.content = (body.content or "").strip() or title.content
    await title.save()

    return {"code": 200, "message": "鎴愬姛", "data": {"id": title_id}}


@router.post("/publish-xiaohongshu")
async def publish_title(
    body: PublishBody,
    user_id: int = Depends(get_current_user_id),
):
    """
    鍙戝竷绗旇鍒板皬绾功锛堟敮鎸佸璐﹀彿鍚屾椂鍙戝竷锛?
    """
    # 楠岃瘉璐﹀彿鍒楄〃涓嶈兘涓虹┖
    if not body.account_ids:
        return {"code": 400, "message": "璇烽€夋嫨鑷冲皯涓€涓彂甯冭处鍙?, "data": None}

    # 楠岃瘉鏍囬鏄惁瀛樺湪
    title_row = await Title.filter(id=body.title_id).first()
    if not title_row:
        return {"code": 404, "message": "鏍囬涓嶅瓨鍦?, "data": None}

    # 楠岃瘉鏍囬鎵€灞炴澘鍧楀睘浜庡綋鍓嶇敤鎴?
    section = await Section.filter(id=title_row.section_id).first()
    if not section or section.user_id != user_id:
        return {"code": 403, "message": "鏃犳潈闄愬彂甯冭鏍囬", "data": None}

    # 鑾峰彇鏍囬瀵瑰簲鐨勬墍鏈夊浘鐗囷紙姝ｆ枃鍥?+ 灏侀潰鍥撅級
    title_images = await TitleImage.filter(title_id=body.title_id).order_by("sort_order")
    if not title_images:
        return {"code": 400, "message": "璇ユ爣棰樹笅娌℃湁鍥剧墖锛岃鍏堜笂浼犲浘鐗?, "data": None}

    # 鏋勫缓鍥剧墖 URL 鍒楄〃
    image_urls = [img.image_url for img in title_images]
    note_title = title_row.title or ""
    note_content = title_row.content or ""

    results = []
    loop = asyncio.get_running_loop()

    for account_id in body.account_ids:
        account_row = await XhsAccount.filter(id=account_id, user_id=user_id).first()
        if not account_row:
            results.append({
                "account_id": account_id, "account_name": "",
                "success": False, "msg": "璐﹀彿涓嶅瓨鍦ㄦ垨鏃犳潈闄?,
            })
            continue

        sync_func = functools.partial(
            publish_xhs_note,
            a1=account_row.a1,
            web_session=account_row.web_session,
            title=note_title,
            content=note_content,
            image_urls=image_urls,
        )

        try:
            publish_result = await loop.run_in_executor(playwright_pool, sync_func)
            logger.info(f"[publish] account={account_id} result={publish_result}")
        except Exception as e:
            logger.error(f"[publish] account={account_id} exception: {e}")
            publish_result = {"success": False, "msg": f"鍙戝竷寮傚父: {repr(e)}", "note_url": None, "data": None}

        if publish_result.get("success"):
            record = await PublishRecord.create(
                user_id=user_id,
                title_id=body.title_id,
                title_title=note_title,
                xhs_id=account_id,
                xhs_name=account_row.name,
                note_url=publish_result.get("note_url", ""),
                platform=1,
                publish_status=2,
                publish_time=datetime.now(),
                content=note_content,
            )
            for img in title_images:
                await PublishImage.create(
                    publish_id=record.id,
                    image_id=img.id,
                    image_url=img.image_url,
                    image_type=img.image_type,
                    sort_order=img.sort_order,
                )
            title_row.status = "2"
            await title_row.save()

            # 鍙戝竷鎴愬姛鍚庤嚜鍔ㄥ瓨鍏ョ礌鏉愬簱锛堝幓閲嶏級
            existing_text = await MaterialText.filter(content=note_content).first()
            if not existing_text:
                await MaterialText.create(
                    user_id=user_id,
                    title=note_title,
                    content=note_content,
                )
            for img in title_images:
                existing_img = await MaterialImage.filter(image_url=img.image_url).first()
                if not existing_img:
                    await MaterialImage.create(user_id=user_id, image_url=img.image_url)

            results.append({
                "account_id": account_id,
                "account_name": account_row.name,
                "success": True,
                "msg": "鍙戝竷鎴愬姛",
                "publish_id": record.id,
                "note_url": publish_result.get("note_url", ""),
            })
        else:
            await PublishRecord.create(
                user_id=user_id,
                title_id=body.title_id,
                xhs_id=account_id,
                platform=1,
                publish_status=3,
                content=note_content,
            )
            results.append({
                "account_id": account_id,
                "account_name": account_row.name,
                "success": False,
                "msg": publish_result.get("msg", "鍙戝竷澶辫触"),
            })

    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count
    message = f"鍙戝竷瀹屾垚锛氭垚鍔?{success_count} 鏉★紝澶辫触 {fail_count} 鏉?

    return {"code": 200, "message": message, "data": {"results": results}}