"""
灏忕孩涔︾瑪璁板彂甯冨伐鍏枫€?

浣跨敤 Playwright 椹卞姩绛惧悕寮曟搸 + xhs 搴撹皟鐢?API锛屽疄鐜板浘鏂囩瑪璁扮殑涓€閿彂甯冦€?
"""
import os
import re
import sys
import json as _json
import asyncio
import tempfile

import requests
from xhs import XhsClient
from xhs.help import sign as _builtin_sign
from playwright.sync_api import sync_playwright


class PlaywrightSigner:
    """绛惧悕杈呭姪绫伙紝鐢ㄦ潵缁曡繃灏忕孩涔︾鍚嶉鎺с€?""

    def __init__(self, a1: str, web_session: str):
        self.a1 = a1
        self.web_session = web_session

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="zh-CN",
        )
        self.context.add_cookies([
            {"name": "a1", "value": a1, "domain": ".xiaohongshu.com", "path": "/"},
            {"name": "web_session", "value": web_session, "domain": ".xiaohongshu.com", "path": "/"},
        ])
        self.page = self.context.new_page()
        self.page.goto(
            "https://www.xiaohongshu.com",
            wait_until="networkidle",
            timeout=30000,
        )
        # 绛夊緟绛惧悕鍑芥暟鍔犺浇灏辩华
        try:
            self.page.wait_for_function(
                "window._webmsxyw != null && typeof window._webmsxyw === 'function'",
                timeout=20000,
            )
        except Exception:
            pass

    def sign(self, uri: str, data=None, a1: str = "", web_session: str = ""):
        """
        鐢熸垚 x-s 绛惧悕銆?

        绛栫暐锛?
        - /upload 鐩稿叧鎺ュ彛锛欽S 鏂扮増绛惧悕 + builtin 鍏滃簳
        - note 鍙戝竷鎺ュ彛锛?web_api/sns/v2/note锛夛細蹇呴』鐢?builtin 鏃х増绛惧悕
          鍘熷洜锛歘webmsxyw 瀵?note 杩斿洖鐨勬槸 2025 骞存柊鐗堢鍚嶆牸寮忥紙XYW_鍓嶇紑鐨?JWT锛夛紝
                浣?/web_api/sns/v2/note 绔偣鍙帴鍙楁棫鐗堢鍚嶏紝JS 绛惧悕浼氳繑鍥?406
        """
        # note 鍙戝竷蹇呴』鐢ㄥ唴缃鍚?
        if "/web_api/sns/v2/note" in uri:
            fallback_data = data if isinstance(data, dict) else None
            try:
                return _builtin_sign(uri, fallback_data, a1=self.a1)
            except Exception:
                return {}

        # 鍏朵粬鎺ュ彛锛欽S 绛惧悕浼樺厛
        if isinstance(data, dict):
            js_data_arg = _json.dumps(data, separators=(",", ":"))
        elif isinstance(data, str):
            js_data_arg = data
        else:
            js_data_arg = '""'

        safe_uri = uri.replace("\\", "\\\\").replace("'", "\\'")

        raw = None
        try:
            raw = self.page.evaluate(
                f"(window._webmsxyw || function(){{}})('{safe_uri}', {js_data_arg})"
            )
        except Exception:
            pass

        if raw and isinstance(raw, dict):
            return {str(k).lower(): str(v) for k, v in raw.items()}

        # JS 澶辫触鍒欑敤 builtin 鍏滃簳
        fallback_data = data if isinstance(data, dict) else None
        try:
            return _builtin_sign(uri, fallback_data, a1=self.a1)
        except Exception:
            return {}

    def close(self):
        try:
            self.browser.close()
        except Exception:
            pass
        try:
            self.playwright.stop()
        except Exception:
            pass


def download_image_to_temp(url: str) -> str | None:
    """
    涓嬭浇缃戠粶鍥剧墖鍒扮郴缁熶复鏃舵枃浠躲€?

    灏忕孩涔︾殑 SDK 鍙戠瑪璁版椂锛屽彧鎺ュ彈鏈湴鐢佃剳涓婄殑鍥剧墖璺緞锛?
    涓嶆帴鍙楃綉椤?URL锛屾墍浠ュ繀椤诲厛鎶婇樋閲屼簯 OSS 涓婄殑鍥句笅杞藉埌鏈湴銆?
    """
    try:
        resp = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            },
            stream=True,
            timeout=15,
        )
        resp.raise_for_status()

        # 鏍规嵁 Content-Type 鑾峰彇鏂囦欢鍚庣紑
        content_type = resp.headers.get("Content-Type", "").split(";")[0].strip()
        ext_map = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "image/bmp": ".bmp",
        }
        ext = ext_map.get(content_type.lower())

        # 濡傛灉 Content-Type 鏃犳硶鍖归厤锛屽垯浠?URL 璺緞鎺ㄦ柇鎵╁睍鍚?
        if not ext:
            m = re.search(r"\.([a-zA-Z]{3,4})$", url.split("?")[0])
            ext = f".{m.group(1).lower()}" if m else ".jpg"

        # 鍏滃簳锛氱‘淇濇墿灞曞悕鍚堟硶
        if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"):
            ext = ".jpg"

        # 鍐欏叆涓存椂鏂囦欢
        # 1. 鍒涘缓涓存椂鏂囦欢锛岃幏鍙栨枃浠舵弿杩扮鍜岃矾寰?
        fd, temp_path = tempfile.mkstemp(suffix=ext)
        # 2. 鐢ㄦ枃浠舵弿杩扮鎵撳紑鏂囦欢锛屽苟鍐欏叆鏂囦欢
        with os.fdopen(fd, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        return temp_path
    except Exception:
        return None


def publish_xhs_note(
    a1: str,
    web_session: str,
    title: str,
    content: str,
    image_urls,
) -> dict:
    """
    鍙戝竷涓€绡囧浘鏂囩瑪璁板埌灏忕孩涔︺€?

    鍙傛暟
    ----
    a1 : str
        灏忕孩涔?cookie a1
    web_session : str
        灏忕孩涔?cookie web_session
    title : str
        绗旇鏍囬
    content : str
        绗旇姝ｆ枃
    image_urls : list[str]
        鍥剧墖 URL 鍒楄〃

    杩斿洖
    ----
    dict : {"success": bool, "msg": str, "note_url": str | None, "data": dict | None}
    """
    # Playwright 鏄悓姝?API锛屽湪 FastAPI锛堝紓姝ワ級鐜涓嬪鏄撳啿绐併€?
    # Windows 涓嬮渶瑕?ProactorEventLoop 绛栫暐鏉ラ伩鍏嶇嚎绋嬪啿绐?
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
    except Exception:
        pass

    # 鏍囧噯鍖?image_urls 涓哄垪琛?
    if isinstance(image_urls, str):
        image_urls = [image_urls]
    if not image_urls:
        return {"success": False, "msg": "鍥剧墖 URL 涓嶈兘涓虹┖", "note_url": None, "data": None}

    # 1. 鍚姩绛惧悕寮曟搸
    try:
        signer = PlaywrightSigner(a1, web_session)
    except Exception as e:
        return {"success": False, "msg": f"绛惧悕寮曟搸鍚姩澶辫触: {repr(e)}", "note_url": None, "data": None}

    # 2. 鍒濆鍖栧皬绾功瀹㈡埛绔?
    cookie = f"a1={a1}; web_session={web_session};"
    try:
        client = XhsClient(cookie, sign=signer.sign)
    except Exception as e:
        signer.close()
        return {"success": False, "msg": f"瀹㈡埛绔垵濮嬪寲澶辫触: {repr(e)}", "note_url": None, "data": None}

    # 3. 涓嬭浇鍥剧墖鍒颁复鏃舵枃浠?
    temp_paths: list[str] = []
    for url in image_urls:
        path = download_image_to_temp(url)
        if not path:
            # 涓嬭浇澶辫触锛屾竻鐞嗗凡涓嬭浇鐨勪复鏃舵枃浠跺悗杩斿洖
            for p in temp_paths:
                try:
                    os.remove(p)
                except Exception:
                    pass
            signer.close()
            return {"success": False, "msg": f"鍥剧墖涓嬭浇澶辫触: {url}", "note_url": None, "data": None}
        temp_paths.append(path)

    # 4. 鍙戝竷绗旇
    try:
        note_info = client.create_image_note(title=title, desc=content, files=temp_paths)
        note_id = note_info.get("id", "") or ""
        note_url = f"https://www.xiaohongshu.com/explore/{note_id}" if note_id else ""
        return {
            "success": True,
            "msg": "鍙戝竷鎴愬姛",
            "note_url": note_url,
            "data": note_info,
        }
    except Exception as e:
        return {"success": False, "msg": f"鍙戝竷杩囩▼鎶ラ敊: {repr(e)}", "note_url": None, "data": None}
    finally:
        signer.close()
        # 娓呯悊涓存椂鏂囦欢
        for p in temp_paths:
            try:
                os.remove(p)
            except Exception:
                pass

