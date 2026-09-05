# 映禾小助手 - Streamlit 单文件应用
# 安装依赖：pip install -r requirements.txt
# 可选增强：pip install yt-dlp（视频下载）；系统安装 ffmpeg（音频提取）
# 运行：streamlit run app.py

import base64
import hmac
import io
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter

st.set_page_config(page_title="映禾小助手", page_icon="🎬", layout="wide")

def config_value(name: str, default: str = ""):
    try:
        return str(st.secrets.get(name, os.getenv(name, default)))
    except Exception:
        return os.getenv(name, default)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Noto+Serif+SC:wght@600;700&display=swap');
:root{--ink:#151329;--muted:#6d6578;--paper:#f7eef1;--line:#e5dce8;--accent:#7226c7;--teal:#24734b}
.stApp{background:linear-gradient(145deg,#c8c0da 0%,#e8cad7 38%,#f7eef1 68%,#fff 100%);color:var(--ink);font-family:'DM Sans','Microsoft YaHei',sans-serif;min-height:100vh}
.block-container{max-width:1180px;padding-top:2rem}
.hero{padding:1.8rem 2.2rem 1.7rem;margin:.4rem 0 1.2rem;border-radius:28px;background:rgba(255,255,255,.58);backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,.82);box-shadow:0 14px 35px rgba(62,35,86,.1)}
.hero h1{font-family:'Noto Serif SC',serif;font-size:2.55rem;letter-spacing:0;margin:0;color:#130c25}
.hero p{margin:.55rem 0 0;color:#514a61;font-size:1.02rem}
.eyebrow{color:var(--accent);font-size:.78rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase}
.panel{background:rgba(255,255,255,.82);backdrop-filter:blur(18px);border:1px solid rgba(255,255,255,.9);border-radius:28px;padding:1.35rem 1.45rem;margin:.8rem 0;box-shadow:0 14px 35px rgba(62,35,86,.12)}
.result{background:rgba(255,255,255,.9);border:1px solid rgba(255,255,255,.95);border-left:4px solid var(--accent);border-radius:22px;padding:1rem 1.1rem;margin:.65rem 0;box-shadow:0 8px 20px rgba(62,35,86,.08)}
.result h3{margin:0 0 .25rem;font-size:1.1rem}.meta{color:var(--muted);font-size:.9rem}
.score{color:var(--teal);font-weight:700;font-size:1.15rem}
.hint{color:var(--muted);font-size:.88rem}
button{border-radius:18px!important}
div.stButton > button{padding:.9rem 1.5rem!important;font-size:1.05rem!important;font-weight:700!important}
.stButton button[kind="primary"]{background:linear-gradient(135deg,#26153c,#6f2f92)!important;border:1px solid rgba(255,255,255,.65)!important;box-shadow:0 10px 24px rgba(56,24,82,.28)!important}
.landing + div .stButton button{background:linear-gradient(135deg,#161222,#3d2457)!important;border:1px solid rgba(255,255,255,.78)!important;border-radius:999px!important;padding:1rem 2.2rem!important;box-shadow:0 12px 26px rgba(36,18,58,.3),inset 0 1px 0 rgba(255,255,255,.25)!important;letter-spacing:.01em}
.stButton button{transition:transform .2s ease,box-shadow .2s ease}.stButton button:hover{transform:translateY(-2px);box-shadow:0 10px 22px rgba(60,30,80,.2)!important}
.tool-nav-bgm button{background:linear-gradient(135deg,#102b49,#217b9d)!important}.tool-nav-font button{background:linear-gradient(135deg,#42194f,#a04f99)!important}
.stTabs [data-baseweb="tab"]{font-size:1.15rem!important;font-weight:700!important;padding:0.7rem 1.2rem!important}
.stTabs [data-baseweb="tab-list"]{gap:.5rem}
.landing{min-height:72vh;border-radius:32px;padding:4rem 5vw;display:flex;align-items:flex-end;background:linear-gradient(120deg,rgba(20,15,35,.78),rgba(93,57,111,.36)),url('https://images.unsplash.com/photo-1492724441997-5dc865305da7?auto=format&fit=crop&w=1800&q=85') center/cover;box-shadow:0 24px 60px rgba(50,25,70,.25);color:#fff}
.landing{animation:heroDrift 10s ease-in-out infinite alternate;background-size:125% auto}.landing h2{animation:riseIn 1.2s ease both}.landing p{animation:riseIn 1.5s .15s ease both}@keyframes heroDrift{from{background-position:35% 48%;filter:saturate(.9)}to{background-position:68% 54%;filter:saturate(1.25)}}@keyframes riseIn{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:translateY(0)}}
.tool-banner{animation:toolPulse 8s ease-in-out infinite alternate;background-size:140% auto!important;background-position:center!important}.bgm-banner{background-image:linear-gradient(120deg,rgba(18,12,35,.82),rgba(76,37,105,.48)),url('https://images.unsplash.com/photo-1516280440614-37939bbacd81?auto=format&fit=crop&w=1800&q=85')!important}.font-banner{background-image:linear-gradient(120deg,rgba(41,24,63,.86),rgba(125,77,145,.5)),url('https://images.unsplash.com/photo-1455390582262-044cdead277a?auto=format&fit=crop&w=1800&q=85')!important}@keyframes toolPulse{from{background-position:38% 48%;filter:saturate(.9)}to{background-position:62% 52%;filter:saturate(1.3)}}
.bgm-progress-banner{color:#fff!important;min-height:194px;display:flex;flex-direction:column;justify-content:center;gap:.55rem}.bgm-progress-banner h2{margin:0;font-size:clamp(1.8rem,3vw,2.45rem);letter-spacing:-.02em}.bgm-progress-banner p{margin:0;color:rgba(255,255,255,.84);font-size:1.02rem}.bgm-progress-meta{display:flex;justify-content:space-between;align-items:center;margin-top:.5rem;font-size:.92rem;font-weight:700;color:rgba(255,255,255,.92)}.bgm-progress-track{height:10px;border-radius:999px;overflow:hidden;background:rgba(255,255,255,.24);box-shadow:inset 0 1px 2px rgba(0,0,0,.2)}.bgm-progress-fill{height:100%;border-radius:inherit;background:linear-gradient(90deg,#b9f3ff 0%,#8ce6ff 45%,#dbb1ff 100%);box-shadow:0 0 16px rgba(160,229,255,.72);transition:width .3s ease}.bgm-progress-steps{display:flex;justify-content:space-between;color:rgba(255,255,255,.62);font-size:.75rem;margin-top:.25rem}.bgm-progress-steps span.is-current{color:#fff}
.music-page{background:linear-gradient(120deg,rgba(21,16,41,.32),rgba(60,27,75,.18)),url('https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b?auto=format&fit=crop&w=1800&q=80') center/cover fixed!important}.type-page{background:linear-gradient(120deg,rgba(37,24,56,.28),rgba(82,50,99,.18)),url('https://images.unsplash.com/photo-1455390582262-044cdead277a?auto=format&fit=crop&w=1800&q=80') center/cover fixed!important}
.tool-choice button{min-height:145px!important;font-size:1.25rem!important;border-radius:24px!important}
.landing h2{font-family:'Noto Serif SC',serif;font-size:clamp(2.6rem,6vw,5.8rem);line-height:1.08;margin:.6rem 0 1rem;max-width:900px}.landing p{font-size:1.1rem;max-width:560px;color:rgba(255,255,255,.82);line-height:1.7}.landing .eyebrow{color:#d7ff8a}
</style>
""", unsafe_allow_html=True)

if "entered" not in st.session_state: st.session_state.entered = False
if "active_tool" not in st.session_state: st.session_state.active_tool = None

access_code = config_value("APP_ACCESS_CODE")
if access_code and not st.session_state.get("authorized", False):
    st.markdown("## 进入映禾工作台")
    st.caption("请输入团队访问口令")
    supplied_code = st.text_input("访问口令", type="password", key="access-code")
    if st.button("进入", type="primary", icon=":material/login:"):
        if hmac.compare_digest(supplied_code, access_code):
            st.session_state.authorized = True
            st.rerun()
        else:
            st.error("访问口令不正确")
    st.stop()

st.markdown('<div class="hero"><div class="eyebrow">YINGHE / CREATOR DESK</div><h1>映禾小助手 — 短视频编导 AI 工作台</h1><p>把繁琐留给工具，把灵感留给创作</p><div class="hint">BGM 识别  专业字体识别</div></div>', unsafe_allow_html=True)

if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "font_history" not in st.session_state:
    st.session_state.font_history = []
if "bgm_library" not in st.session_state:
    st.session_state.bgm_library = []
if "font_library" not in st.session_state:
    st.session_state.font_library = []

if not st.session_state.entered:
    st.markdown('''<section class="landing"><div><div class="eyebrow">映禾剪辑工作室 · CREATIVE TOOLKIT</div><h2>把繁琐留给工具，<br>把灵感留给创作</h2><p>映禾小助手为短视频编导与剪辑师提供 BGM 识别、音轨处理与专业字体识别，让每一次创作都更快找到节奏与表达。</p></div></section>''', unsafe_allow_html=True)
    st.markdown("### 映禾剪辑工作室")
    st.markdown("<div class='hint' style='font-size:1rem'>Inher Video Editing Studio</div>", unsafe_allow_html=True)
    st.write("告别下班后的二次加班，您省下精力，我剪出惊喜。我们专注于短视频内容策划、剪辑与视觉包装，把经验沉淀成可复用的创作工具。")
    if st.button("进入映禾工作台  →", type="primary"):
        st.session_state.entered = True
        st.rerun()
    st.stop()

def copy_button(text: str, key: str, label: str):
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    st.markdown(f"<script>window.__yhCopy=window.__yhCopy||{{}};window.__yhCopy['{key}']=atob('{encoded}');</script>", unsafe_allow_html=True)
    if st.button(label, key=key):
        st.code(text, language=None)
        st.info("已准备复制内容：请点击代码框右上角复制。")


def render_bgm_header(percent: int = 0, step: str = "等待开始") -> str:
    """Build the BGM workspace banner and its in-banner progress indicator."""
    percent = max(0, min(100, int(percent)))
    stages = [(25, "提取音频"), (50, "分离人声"), (75, "增加音量"), (100, "交叉识别")]
    step_markup = "".join(
        f"<span class='{'is-current' if percent >= value else ''}'>{label}</span>"
        for value, label in stages
    )
    return (
        "<div class='panel tool-banner bgm-banner bgm-progress-banner'>"
        "<h2>🎵 BGM 识别工作区</h2>"
        "<p>提取音频 · 分离人声 · 增加音量 · 交叉识别</p>"
        f"<div class='bgm-progress-meta'><span>{step}</span><span>{percent}%</span></div>"
        f"<div class='bgm-progress-track' role='progressbar' aria-valuemin='0' aria-valuemax='100' aria-valuenow='{percent}'><div class='bgm-progress-fill' style='width:{percent}%'></div></div>"
        f"<div class='bgm-progress-steps'>{step_markup}</div>"
        "</div>"
    )

if st.session_state.entered and st.session_state.active_tool is None:
    st.markdown("<style>.stApp{background:linear-gradient(145deg,#c8c0da 0%,#e8cad7 42%,#fff 100%)}.st-key-enter-bgm button,.st-key-enter-font button{width:100%!important;min-height:72px!important;border-radius:22px!important;padding:1rem 1.5rem!important;box-shadow:0 14px 28px rgba(49,22,74,.2)!important;color:#fff!important}.st-key-enter-bgm button{background:linear-gradient(135deg,#123b5a,#1d8a9b)!important}.st-key-enter-font button{background:linear-gradient(135deg,#47204f,#a05291)!important}.st-key-enter-bgm button p,.st-key-enter-font button p{font-size:25px!important;font-weight:700!important;color:#fff!important}.st-key-back-home-bottom{margin-top:0}.st-key-back-home-bottom button{min-height:34px!important;width:38px!important;border-radius:50%!important;padding:0!important;background:rgba(255,255,255,.78)!important;color:#21152e!important;box-shadow:0 6px 14px rgba(49,22,74,.15)!important}.st-key-back-home-bottom button p{font-size:18px!important}</style>", unsafe_allow_html=True)
    st.markdown("## 选择创作工具")
    st.caption("选择一个工作区，进入完整功能")
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("🎵 进入 BGM 识别", width="stretch", type="primary", key="enter-bgm"):
            st.session_state.bgm_progress = 0
            st.session_state.bgm_progress_step = "等待开始"
            st.session_state.active_tool = "bgm"; st.rerun()
    with nav2:
        if st.button("字体识别", width="stretch", type="secondary", key="enter-font"):
            st.session_state.active_tool = "font"; st.rerun()
    st.markdown("<div style='height:28vh'></div>", unsafe_allow_html=True)
    if st.button("←", key="back-home-bottom", help="返回主页"):
        st.session_state.entered = False; st.session_state.active_tool = None; st.rerun()
    st.stop()

if st.session_state.entered and st.session_state.active_tool:
    if st.session_state.active_tool == "bgm":
        st.markdown("<style>.stApp{background:linear-gradient(120deg,rgba(21,16,41,.3),rgba(60,27,75,.16)),url('https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=1800&q=80') center/cover fixed}</style>", unsafe_allow_html=True)
    else:
        st.markdown("<style>.stApp{background:linear-gradient(120deg,rgba(37,24,56,.24),rgba(82,50,99,.14)),url('https://images.unsplash.com/photo-1455390582262-044cdead277a?auto=format&fit=crop&w=1800&q=80') center/cover fixed}</style>", unsafe_allow_html=True)
    if st.button("← 返回工具选择", key="back-tools"):
        st.session_state.active_tool = None; st.rerun()
    bgm_header_slot = None
    if st.session_state.active_tool == "bgm":
        bgm_header_slot = st.empty()
        bgm_header_slot.markdown(
            render_bgm_header(
                st.session_state.get("bgm_progress", 0),
                st.session_state.get("bgm_progress_step", "等待开始"),
            ),
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<div class='panel tool-banner font-banner' style='color:white'><h2>字体识别工作区</h2><p>上传截图，找到最接近的字体并管理爆款字体库</p></div>", unsafe_allow_html=True)


def update_bgm_progress(percent: int, step: str):
    """Persist and redraw the in-banner BGM pipeline progress."""
    st.session_state.bgm_progress = max(0, min(100, int(percent)))
    st.session_state.bgm_progress_step = step
    if bgm_header_slot is not None:
        bgm_header_slot.markdown(render_bgm_header(percent, step), unsafe_allow_html=True)


def _configured_api():
    """Return the configured recognition endpoint and token.

    AUDD_* is the recommended naming. SHAZAM_* remains supported so existing
    Streamlit secrets do not need to be renamed immediately.
    """
    api = config_value("AUDD_API_URL") or config_value("SHAZAM_API_URL") or "https://api.audd.io/"
    token = config_value("AUDD_API_TOKEN") or config_value("SHAZAM_API_KEY")
    return api, token


def _require_binary(name: str, default_binary: str, label: str) -> str:
    binary = config_value(name, default_binary)
    if not shutil.which(binary):
        raise RuntimeError(f"云端未找到 {label}，请在项目根目录的 packages.txt 中安装后重新部署")
    return binary


def extract_audio_bytes(video_bytes: bytes, suffix: str = ".mp4") -> bytes:
    """Convert an uploaded video/audio file to mono WAV for recognition."""
    ffmpeg = _require_binary("FFMPEG_PATH", "ffmpeg", "ffmpeg")
    with tempfile.TemporaryDirectory() as td:
        source = Path(td) / f"source{suffix}"
        audio = Path(td) / "audio.wav"
        source.write_bytes(video_bytes)
        try:
            subprocess.run(
                [ffmpeg, "-y", "-i", str(source), "-t", "30", "-vn", "-af", "loudnorm", "-ac", "1", "-ar", "22050", str(audio)],
                check=True,
                capture_output=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("视频处理超时，请裁剪后上传 3 分钟以内的片段") from exc
        except subprocess.CalledProcessError as exc:
            raise RuntimeError("无法读取这个媒体文件，请换用 MP3、M4A、WAV、MP4 或 MOV 格式") from exc
        return audio.read_bytes()


def download_and_extract(url: str, platform: str = "抖音 Douyin") -> bytes:
    """Download one public video and extract its audio track."""
    ytdlp = _require_binary("YTDLP_PATH", "yt-dlp", "yt-dlp")
    referers = {
        "抖音 Douyin": "https://www.douyin.com/",
        "TikTok": "https://www.tiktok.com/",
        "YouTube / Shorts": "https://www.youtube.com/",
    }
    with tempfile.TemporaryDirectory() as td:
        output = Path(td) / "video.%(ext)s"
        try:
            subprocess.run(
                [
                    ytdlp,
                    "--no-playlist",
                    "--format", "bestaudio/best",
                    "--retries", "3",
                    "--fragment-retries", "3",
                    "--socket-timeout", "30",
                    "--max-filesize", "50M",
                    "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131 Safari/537.36",
                    "--referer", referers.get(platform, "https://www.google.com/"),
                    "-o", str(output), url,
                ],
                check=True,
                capture_output=True,
                timeout=180,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("链接下载超时，建议直接上传音频或视频文件") from exc
        except subprocess.CalledProcessError as exc:
            error_text = (exc.stderr or b"").decode("utf-8", errors="ignore").lower()
            if any(word in error_text for word in ("login", "sign in", "cookie", "验证码", "private video")):
                raise RuntimeError(f"{platform} 要求登录或验证码，云端无法读取；请直接上传视频或音频文件") from exc
            if "unsupported url" in error_text:
                raise RuntimeError("暂不支持这个分享链接格式，请复制平台的完整公开链接，或直接上传文件") from exc
            raise RuntimeError(f"{platform} 暂时拒绝云端下载该链接，请直接上传视频或音频文件") from exc
        sources = [p for p in Path(td).glob("video.*") if p.is_file()]
        if not sources:
            raise RuntimeError("没有从链接中下载到可处理的视频音频")
        return extract_audio_bytes(sources[0].read_bytes(), sources[0].suffix)


def _find_media_url(payload):
    """Find a media URL in common resolver response shapes."""
    preferred_keys = (
        "media_url", "video_url", "audio_url", "download_url", "download", "play",
        "play_url", "play_addr", "no_watermark_url", "url_list",
    )
    if isinstance(payload, dict):
        for key in preferred_keys:
            value = payload.get(key)
            if isinstance(value, str) and re.match(r"^https?://", value, re.I):
                return value
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and re.match(r"^https?://", item, re.I):
                        return item
                    found = _find_media_url(item)
                    if found:
                        return found
            if isinstance(value, dict):
                found = _find_media_url(value)
                if found:
                    return found
        for value in payload.values():
            found = _find_media_url(value)
            if found:
                return found
        value = payload.get("url")
        if isinstance(value, str) and re.match(r"^https?://", value, re.I):
            return value
    elif isinstance(payload, list):
        for value in payload:
            found = _find_media_url(value)
            if found:
                return found
    return ""


def _download_resolved_media(media_url: str) -> bytes:
    """Download a resolver-provided media URL with a conservative size cap."""
    if not re.match(r"^https://", media_url, re.I):
        raise RuntimeError("解析服务返回的媒体地址不是安全的 HTTPS 链接")
    try:
        response = requests.get(media_url, timeout=120, stream=True)
        response.raise_for_status()
        max_bytes = 220 * 1024 * 1024
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > max_bytes:
            raise ValueError("解析后的视频超过 220MB，请换一条较短的视频")
        chunks = []
        total = 0
        for chunk in response.iter_content(1024 * 1024):
            if not chunk:
                continue
            total += len(chunk)
            if total > max_bytes:
                raise ValueError("解析后的视频超过 220MB，请换一条较短的视频")
            chunks.append(chunk)
        return b"".join(chunks)
    except requests.Timeout as exc:
        raise RuntimeError("解析服务返回媒体超时，请稍后重试") from exc


def resolve_and_extract(url: str, platform: str) -> bytes:
    """Resolve a sharing-page URL through a configured cloud media provider.

    ``post_json`` is the default contract used by a custom resolver. Set
    ``MEDIA_RESOLVER_MODE=rapidapi_get`` for RapidAPI or ``tikhub_get`` for
    TikHub's Bearer-token GET endpoint.
    """
    resolver_api = config_value("MEDIA_RESOLVER_API_URL")
    if not resolver_api:
        raise RuntimeError(
            "还没有配置云端链接解析服务。请在 Streamlit Cloud Secrets 中填写 MEDIA_RESOLVER_API_URL 和 MEDIA_RESOLVER_API_KEY"
        )
    if not re.match(r"^https://", resolver_api, re.I):
        raise RuntimeError("MEDIA_RESOLVER_API_URL 必须使用 HTTPS")
    resolver_key = config_value("MEDIA_RESOLVER_API_KEY")
    resolver_mode = config_value("MEDIA_RESOLVER_MODE", "post_json").strip().lower()
    url_param = config_value("MEDIA_RESOLVER_URL_PARAM", "url").strip() or "url"
    headers = {"Accept": "application/json"}
    rapidapi_get = resolver_mode in {"rapidapi", "rapidapi_get"}
    bearer_get = resolver_mode in {"tikhub", "tikhub_get", "bearer_get", "get"}
    if rapidapi_get:
        if resolver_key:
            headers["X-RapidAPI-Key"] = resolver_key
        resolver_host = config_value("MEDIA_RESOLVER_API_HOST")
        if resolver_host:
            headers["X-RapidAPI-Host"] = resolver_host
    elif bearer_get:
        if resolver_key:
            headers["Authorization"] = f"Bearer {resolver_key}"
    elif resolver_key:
        headers["Authorization"] = f"Bearer {resolver_key}"
        headers["X-API-Key"] = resolver_key
    try:
        if rapidapi_get or bearer_get:
            response = requests.get(
                resolver_api,
                params={url_param: url},
                headers=headers,
                timeout=60,
            )
        elif resolver_mode in {"post_form", "form"}:
            response = requests.post(
                resolver_api,
                data={url_param: url, "platform": platform},
                headers=headers,
                timeout=60,
            )
        else:
            response = requests.post(
                resolver_api,
                json={"url": url, "platform": platform},
                headers=headers,
                timeout=60,
            )
        response.raise_for_status()
        media_url = _find_media_url(response.json())
    except requests.Timeout as exc:
        raise RuntimeError("云端链接解析服务响应超时，请稍后重试") from exc
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "未知"
        raise RuntimeError(f"云端链接解析服务请求失败：HTTP {status}") from exc
    except ValueError as exc:
        raise RuntimeError("云端链接解析服务返回的数据格式无法识别") from exc
    if not media_url:
        raise RuntimeError("云端链接解析服务没有返回可下载的音视频地址")
    suffix = Path(media_url.split("?", 1)[0]).suffix.lower() or ".mp4"
    return extract_audio_bytes(_download_resolved_media(media_url), suffix)


def _recognition_result(payload: dict):
    if payload.get("status") == "error":
        error = payload.get("error") or {}
        message = error.get("error_message") or error.get("message") or "识别服务返回错误"
        raise RuntimeError(message)
    result = payload.get("result") or {}
    if not result:
        raise RuntimeError("没有识别到歌曲，请换一段更清晰、时长更长的音频")
    artwork = ""
    apple = result.get("apple_music") or {}
    artwork_data = apple.get("artwork") or {}
    if isinstance(artwork_data, dict):
        artwork = artwork_data.get("url") or ""
        artwork = artwork.replace("{w}", "600").replace("{h}", "600")
    if not artwork:
        spotify = result.get("spotify") or {}
        album = spotify.get("album") or {}
        images = album.get("images") or []
        if images:
            artwork = images[0].get("url") or ""
    return {
        "title": result.get("title") or "未知歌曲",
        "artist": result.get("artist") or "未知歌手",
        "artwork": artwork,
        "song_link": result.get("song_link") or "",
    }


def recognize_audio(data: bytes, filename: str):
    api, token = _configured_api()
    if not token:
        raise RuntimeError("还没有配置 AudD API Token。请在 Streamlit Cloud 的 Settings → Secrets 中填写 AUDD_API_TOKEN")
    if len(data) > 9 * 1024 * 1024:
        raise ValueError("提交识别的音频超过 9MB，请上传更短的片段")
    if "audd.io" in api.lower():
        response = requests.post(
            api,
            data={"api_token": token, "return": "apple_music,spotify"},
            files={"file": (filename, data)},
            timeout=60,
        )
    else:
        response = requests.post(api, headers={"X-API-Key": token}, files={"file": (filename, data)}, timeout=60)
    response.raise_for_status()
    result = _recognition_result(response.json())
    return result["title"], result["artist"], False, result["artwork"], result["song_link"]


def parse_bgm(url: str, platform: str):
    if not re.match(r"^https?://", url, re.I):
        raise ValueError("链接需要以 http:// 或 https:// 开头")
    data = download_and_extract(url, platform)
    title, artist, demo, artwork, song_link = recognize_audio(data, "bgm.wav")
    return data, title, artist, demo, artwork, song_link

def font_results(image: Image.Image):
    api = config_value("FONT_API_URL", "https://fonts.free/api/identify/?top=5")
    key = config_value("FONT_API_KEY")
    b = io.BytesIO()
    image.convert("RGB").save(b, format="JPEG", quality=88, optimize=True)
    headers = {"X-Api-Key": key} if key else {}
    response = requests.post(
        api,
        headers=headers,
        files={"image": ("font.jpg", b.getvalue(), "image/jpeg")},
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    raw_items = payload.get("matches") or payload.get("results") or []
    if not raw_items:
        raise RuntimeError("没有找到相似字体，请裁剪到一行清晰文字后重试")
    items = []
    for match in raw_items[:5]:
        raw_score = match.get("score", match.get("confidence", 0))
        try:
            numeric_score = float(raw_score)
        except (TypeError, ValueError):
            numeric_score = 0
        if 0 <= numeric_score <= 1:
            numeric_score *= 100
        items.append({
            "name": match.get("family") or match.get("name") or "未知字体",
            "score": max(0, min(100, round(numeric_score))),
            "scene": match.get("category") or "相似开源字体",
            "url": match.get("url") or match.get("source_url") or "",
        })
    return items, False

def render_font_workspace():
    uploaded = st.file_uploader("上传字体截图", type=["jpg","jpeg","png"], key="font_image")
    image = None
    if uploaded:
        if uploaded.size > 10 * 1024 * 1024: st.error("图片不能超过 10MB")
        else:
            try: image = Image.open(uploaded).convert("RGB"); st.image(image, caption="截图预览", width=560)
            except Exception as e: st.error(f"图片读取失败：{e}")
    if st.button("🔍 开始识别字体", type="primary", key="font-action"):
        if image is None: st.error("请先上传有效的 JPG 或 PNG 图片")
        else:
            try:
                prep = ImageEnhance.Contrast(image.convert("L")).enhance(1.35).filter(ImageFilter.SHARPEN)
                st.session_state.fonts = font_results(prep)
                top_name = st.session_state.fonts[0][0]["name"]
                st.session_state.font_history.insert(0, {"name": top_name, "time": datetime.now().strftime("%H:%M:%S")})
            except Exception as e: st.error(f"识别失败：{e}")
    if "fonts" in st.session_state:
        results, demo = st.session_state.fonts
        for i, item in enumerate(results, 1):
            st.markdown(f'<div class="result"><div class="meta">TOP {i}</div><h3>{item["name"]}</h3><div class="score">匹配度 {item["score"]}%</div><div class="hint">建议场景：{item["scene"]}</div></div>', unsafe_allow_html=True)
            if item.get("url"): st.link_button("查看字体", item["url"], icon=":material/open_in_new:")
            copy_button(item["name"], f"copy-font-new-{i}", "📋 复制字体名称")
    st.markdown("### 字体识别历史")
    st.metric("累计识别次数", len(st.session_state.font_history))
    if st.session_state.font_history:
        counts = {}
        for item in st.session_state.font_history: counts[item["name"]] = counts.get(item["name"], 0) + 1
        st.caption("搜索最多")
        for name, count in sorted(counts.items(), key=lambda x: x[1], reverse=True): st.markdown(f"- **{name}** · {count} 次")
    else: st.caption("暂无字体识别记录，完成一次识别后会显示在这里。")
    st.markdown("### 爆款字体")
    with st.expander("＋ 手动添加爆款字体"):
        ft = st.text_input("字体名称", key="font_lib_name_new"); fs = st.text_input("建议使用场景", key="font_lib_scene_new")
        fc = st.selectbox("分类", ["标题高亮", "手写情绪", "知识口播", "品牌包装", "待整理"], key="font_lib_cat_new")
        fi = st.file_uploader("上传字体示例图片", type=["jpg","jpeg","png"], key="font_lib_img_new")
        if st.button("保存到字体库", key="save-font-lib-new"):
            if ft.strip(): st.session_state.font_library.insert(0, {"name":ft.strip(),"scene":fs.strip() or "待补充","category":fc,"image":fi.getvalue() if fi else None}); st.success("已保存到爆款字体库")
            else: st.warning("请填写字体名称")
    if st.session_state.font_library:
        ff = st.selectbox("按分类查看字体", ["全部"] + sorted({x["category"] for x in st.session_state.font_library}), key="font-lib-filter-new")
        for item in st.session_state.font_library:
            if ff != "全部" and item["category"] != ff: continue
            st.markdown(f"**{item['name']}** · {item['scene']} · `#{item['category']}`")
            if item["image"]: st.image(item["image"], width=260)

if st.session_state.entered and st.session_state.active_tool == "font":
    render_font_workspace()
    st.stop()

tab1 = st.tabs(["🎵 BGM 识别"])[0]
with tab1:
    st.markdown('<div class="panel"><div class="eyebrow">01 / AUDIO</div>', unsafe_allow_html=True)
    platform = st.selectbox("选择视频平台", ["抖音 Douyin", "TikTok", "YouTube / Shorts"])
    url = st.text_input("请粘贴视频分享链接", placeholder="https://v.douyin.com/...", key="video_url")
    uploaded_audio = st.file_uploader("或直接上传待识别音频（推荐）", type=["mp3", "wav", "m4a"], key="bgm_audio")
    uploaded_video = st.file_uploader("或上传视频自动提取 BGM", type=["mp4", "mov", "mkv", "webm"], key="bgm_video")
    st.caption("上传视频或粘贴公开链接后，系统会自动提取并标准化音量，再提交 AudD 识别。")
    if config_value("MEDIA_RESOLVER_API_URL"):
        st.caption("已启用云端链接解析：粘贴抖音分享页后，会先解析媒体地址再处理。")
    else:
        st.caption("提示：抖音分享页需要配置云端链接解析服务；未配置时请直接上传视频或音频。")
    
    if st.button("🚀 开始 BGM 识别", type="primary"):
        if not url.strip() and not uploaded_audio and not uploaded_video: st.error("请粘贴视频链接，或上传音频/视频文件")
        else:
            try:
                # The progress indicator lives in the rounded workspace banner
                # so the current stage remains visible while the form is busy.
                update_bgm_progress(0, "准备提取音频")
                with st.spinner("正在处理音频并识别歌曲…"):
                    if uploaded_audio:
                        if uploaded_audio.size > 50 * 1024 * 1024:
                            raise ValueError("音频文件不能超过 50MB")
                        suffix = Path(uploaded_audio.name).suffix.lower() or ".mp3"
                        audio = extract_audio_bytes(uploaded_audio.getvalue(), suffix)
                    elif uploaded_video:
                        if uploaded_video.size > 200 * 1024 * 1024:
                            raise ValueError("视频文件不能超过 200MB")
                        suffix = Path(uploaded_video.name).suffix.lower() or ".mp4"
                        audio = extract_audio_bytes(uploaded_video.getvalue(), suffix)
                    else:
                        if config_value("MEDIA_RESOLVER_API_URL"):
                            audio = resolve_and_extract(url.strip(), platform)
                        else:
                            audio = download_and_extract(url.strip(), platform)
                    update_bgm_progress(25, "提取音频")
                    update_bgm_progress(50, "分离人声")
                    update_bgm_progress(75, "增加音量")
                    title, artist, demo, artwork, song_link = recognize_audio(audio, "bgm.wav")
                st.session_state.bgm = {
                    "audio": audio,
                    "title": title,
                    "artist": artist,
                    "artwork": artwork,
                    "song_link": song_link,
                }
                update_bgm_progress(100, "交叉识别完成")
                st.session_state.search_history.insert(0, {"platform": platform.split()[0] if url.strip() else ("视频上传" if uploaded_video else "音频上传"), "query": url.strip() or (uploaded_video.name if uploaded_video else uploaded_audio.name), "title": title, "artist": artist, "audio": audio, "artwork": artwork, "song_link": song_link})
            except requests.Timeout: st.error("识别服务响应超时，请稍后再试")
            except requests.HTTPError as e: st.error(f"识别服务请求失败：HTTP {e.response.status_code}")
            except Exception as e: st.error(f"识别失败：{e}")
    st.markdown('</div>', unsafe_allow_html=True)
    if "bgm" in st.session_state:
        result = st.session_state.bgm
        audio, title, artist = result["audio"], result["title"], result["artist"]
        st.audio(audio, format="audio/wav")
        if result.get("artwork"):
            st.image(result["artwork"], caption="歌曲封面", width=180)
        st.markdown(f'<div class="result"><div class="meta">识别结果</div><h3>《{title}》</h3><div class="meta">歌手 / 艺术家：{artist}</div></div>', unsafe_allow_html=True)
        if result.get("song_link"):
            st.link_button("打开歌曲页面", result["song_link"], icon=":material/open_in_new:")
        copy_button(f"{artist} - {title}", "copy-song", "📋 一键复制歌名")
    st.markdown("### 搜索历史")
    st.metric("累计识别次数", len(st.session_state.search_history))
    if st.session_state.search_history:
        for item in st.session_state.search_history[:8]:
            st.markdown(f"- **{item['platform']}** · {item['artist']} - {item['title']} · `{item['query'][:42]}`")
            hcol1, hcol2, hcol3 = st.columns([1.4, 1, 1])
            with hcol1:
                if item.get("artwork"): st.image(item["artwork"], width=120)
                st.audio(item["audio"], format="audio/wav")
            with hcol2:
                st.download_button("⬇️ 下载 BGM", data=item["audio"], file_name=f"{item['title']}.wav", mime="audio/wav", key=f"dl-{id(item)}")
            with hcol3:
                q = requests.utils.quote(f"{item['artist']} {item['title']}")
                st.markdown(f"[网易云音乐 ↗](https://music.163.com/#/search/m/?s={q}&type=1)  \n[QQ 音乐 ↗](https://y.qq.com/n/ryqq/search?w={q})")
    else:
        st.caption("暂无搜索记录，完成一次 BGM 识别后会显示在这里。")
    st.markdown("### 爆款 BGM")
    with st.expander("＋ 手动添加 BGM"):
        search_word = st.text_input("先搜索音乐（可选）", placeholder="输入歌名或歌手", key="lib_search")
        if search_word.strip():
            sq = requests.utils.quote(search_word.strip())
            st.markdown(f"[在网易云音乐搜索 ↗](https://music.163.com/#/search/m/?s={sq}&type=1)　[在 QQ 音乐搜索 ↗](https://y.qq.com/n/ryqq/search?w={sq})")
        lt = st.text_input("BGM 名称", key="lt"); la = st.text_input("歌手 / 来源", key="la")
        lc = st.selectbox("分类", ["情绪氛围", "卡点燃向", "探店同城", "生活方式", "口播配乐", "待整理"], key="lc")
        lf = st.file_uploader("上传音频（可选）", type=["mp3", "wav", "m4a"], key="lf")
        if st.button("保存到 BGM 库", key="save-lib"):
            if lt.strip(): st.session_state.bgm_library.insert(0, {"title":lt.strip(),"artist":la.strip() or "未知","category":lc,"audio":lf.getvalue() if lf else None}); st.success("已保存")
            else: st.warning("请填写 BGM 名称")
    if st.session_state.bgm_library:
        filt = st.selectbox("按分类查看", ["全部"] + sorted({x["category"] for x in st.session_state.bgm_library}), key="lib-filter")
        for item in st.session_state.bgm_library:
            if filt != "全部" and item["category"] != filt: continue
            st.markdown(f"**{item['title']}** · {item['artist']} · `#{item['category']}`")
            if item["audio"]: st.audio(item["audio"], format="audio/wav")
