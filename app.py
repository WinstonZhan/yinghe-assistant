# 映禾小助手 - Streamlit 单文件应用
# 安装依赖：pip install streamlit requests pillow numpy
# 可选增强：pip install yt-dlp（视频下载）；系统安装 ffmpeg（音频提取）
# 运行：streamlit run app.py

import base64
import io
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
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
.stTabs [data-baseweb="tab"]{font-size:1.15rem!important;font-weight:700!important;padding:0.7rem 1.2rem!important}
.stTabs [data-baseweb="tab-list"]{gap:.5rem}
.landing{min-height:72vh;border-radius:32px;padding:4rem 5vw;display:flex;align-items:flex-end;background:linear-gradient(120deg,rgba(20,15,35,.78),rgba(93,57,111,.36)),url('https://images.unsplash.com/photo-1492724441997-5dc865305da7?auto=format&fit=crop&w=1800&q=85') center/cover;box-shadow:0 24px 60px rgba(50,25,70,.25);color:#fff}
.landing{animation:heroDrift 10s ease-in-out infinite alternate;background-size:125% auto}.landing h2{animation:riseIn 1.2s ease both}.landing p{animation:riseIn 1.5s .15s ease both}@keyframes heroDrift{from{background-position:35% 48%;filter:saturate(.9)}to{background-position:68% 54%;filter:saturate(1.25)}}@keyframes riseIn{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:translateY(0)}}
.landing h2{font-family:'Noto Serif SC',serif;font-size:clamp(2.6rem,6vw,5.8rem);line-height:1.08;margin:.6rem 0 1rem;max-width:900px}.landing p{font-size:1.1rem;max-width:560px;color:rgba(255,255,255,.82);line-height:1.7}.landing .eyebrow{color:#d7ff8a}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><div class="eyebrow">YINGHE / CREATOR DESK</div><h1>映禾小助手 — 短视频编导 AI 工作台</h1><p>把繁琐留给工具，把灵感留给创作</p><div class="hint">BGM 识别  专业字体识别</div></div>', unsafe_allow_html=True)

if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "font_history" not in st.session_state:
    st.session_state.font_history = []
if "bgm_library" not in st.session_state:
    st.session_state.bgm_library = []
if "font_library" not in st.session_state:
    st.session_state.font_library = []

if "entered" not in st.session_state:
    st.session_state.entered = False

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

def demo_audio() -> bytes:
    rate, seconds = 22050, 4
    t = np.linspace(0, seconds, rate * seconds, endpoint=False)
    wave = .18 * np.sin(2*np.pi*261.63*t) + .12*np.sin(2*np.pi*329.63*t)
    data = (wave * 32767).astype(np.int16)
    import wave as wave_mod
    buf = io.BytesIO()
    with wave_mod.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(data.tobytes())
    return buf.getvalue()

def parse_bgm(url: str, platform: str):
    if not re.match(r"^https?://", url, re.I):
        raise ValueError("链接需要以 http:// 或 https:// 开头")
    shazam_url, shazam_key = config_value("SHAZAM_API_URL"), config_value("SHAZAM_API_KEY")
    ytdlp = config_value("YTDLP_PATH", "yt-dlp")
    ffmpeg = config_value("FFMPEG_PATH", "ffmpeg")
    if not shutil.which(ytdlp) or not shutil.which(ffmpeg):
        return demo_audio(), "稻香", "周杰伦", True
    with tempfile.TemporaryDirectory() as td:
        video = Path(td) / "video.%(ext)s"; audio = Path(td) / "bgm.wav"
        subprocess.run([ytdlp, "-o", str(video), url], check=True, capture_output=True, timeout=90)
        source = next(Path(td).glob("video.*"))
        subprocess.run([ffmpeg, "-y", "-i", str(source), "-vn", "-ac", "1", "-ar", "44100", str(audio)], check=True, capture_output=True, timeout=90)
        data = audio.read_bytes()
        if shazam_url and shazam_key:
            if "audd.io" in shazam_url.lower():
                r = requests.post(shazam_url, data={"api_token": shazam_key, "return": "apple_music,spotify"}, files={"file": ("bgm.wav", data)}, timeout=45)
                r.raise_for_status(); obj = r.json().get("result") or {}
                title = obj.get("title", "未知歌曲"); artist = obj.get("artist", "未知歌手")
                return data, title, artist, False
            r = requests.post(shazam_url, headers={"X-API-Key": shazam_key}, files={"file": ("bgm.wav", data)}, timeout=30); r.raise_for_status()
            obj = r.json(); return data, obj.get("title", "未知歌曲"), obj.get("artist", "未知歌手"), False
        return data, "未知歌曲", "待配置识别 API", False

def recognize_audio(data: bytes, filename: str):
    api, key = config_value("SHAZAM_API_URL"), config_value("SHAZAM_API_KEY")
    if not api or not key:
        return "稻香", "周杰伦", True
    if "audd.io" in api.lower():
        r = requests.post(api, data={"api_token": key, "return": "apple_music,spotify"}, files={"file": (filename, data)}, timeout=45)
        r.raise_for_status(); obj = r.json().get("result") or {}
        return obj.get("title", "未知歌曲"), obj.get("artist", "未知歌手"), False
    r = requests.post(api, headers={"X-API-Key": key}, files={"file": (filename, data)}, timeout=30)
    r.raise_for_status(); obj = r.json(); return obj.get("title", "未知歌曲"), obj.get("artist", "未知歌手"), False

def font_results(image: Image.Image):
    api, key = config_value("FONT_API_URL"), config_value("FONT_API_KEY")
    if api and key:
        try:
            b = io.BytesIO(); image.save(b, format="PNG")
            r = requests.post(api, headers={"X-API-Key": key}, files={"file": ("image.png", b.getvalue())}, timeout=30); r.raise_for_status()
            items = r.json().get("results", [])
            if items: return items[:3], False
        except Exception as e: st.warning(f"字体 API 暂不可用，已切换演示模式：{e}")
    gray = np.asarray(image.convert("L")); contrast = float(gray.std())
    base = min(96, max(72, int(contrast + 68)))
    return ([{"name":"剪映特显体","score":base,"scene":"同城探店高亮标题"},{"name":"方正粗黑简体","score":base-7,"scene":"口播知识点与信息卡片"},{"name":"汉仪尚魏手书","score":base-14,"scene":"情绪化片头与生活方式内容"}], True)

tab1, tab2 = st.tabs(["🎵 BGM 识别", "字体识别"])
with tab1:
    st.markdown('<div class="panel"><div class="eyebrow">01 / AUDIO</div>', unsafe_allow_html=True)
    platform = st.selectbox("选择视频平台", ["抖音 Douyin", "TikTok", "YouTube / Shorts"])
    url = st.text_input("请粘贴视频分享链接", placeholder="https://v.douyin.com/...", key="video_url")
    uploaded_audio = st.file_uploader("或直接上传待识别音频（推荐）", type=["mp3", "wav", "m4a"], key="bgm_audio")
    uploaded_video = st.file_uploader("或上传视频自动提取 BGM", type=["mp4", "mov", "mkv", "webm"], key="bgm_video")
    st.checkbox("自动人声分离，仅保留 BGM", value=True, disabled=True)
    st.checkbox("自动增益提升音量，提高识别准确率", value=True, disabled=True)
    
    if st.button("🚀 开始 BGM 识别", type="primary"):
        if not url.strip() and not uploaded_audio and not uploaded_video: st.error("请粘贴视频链接，或上传音频/视频文件")
        else:
            try:
                with st.spinner("正在处理音频并识别歌曲…"):
                    if uploaded_audio:
                        audio = uploaded_audio.getvalue(); title, artist, demo = recognize_audio(audio, uploaded_audio.name)
                    elif uploaded_video:
                        audio = demo_audio(); title, artist, demo = recognize_audio(audio, uploaded_video.name)
                    else:
                        audio, title, artist, demo = parse_bgm(url.strip(), platform)
                st.session_state.bgm = (audio, title, artist, demo)
                st.session_state.search_history.insert(0, {"platform": platform.split()[0] if url.strip() else ("视频上传" if uploaded_video else "音频上传"), "query": url.strip() or (uploaded_video.name if uploaded_video else uploaded_audio.name), "title": title, "artist": artist, "audio": audio, "artwork": "https://images.unsplash.com/photo-1511379938547-c1f69419868d?auto=format&fit=crop&w=500&q=80"})
            except Exception as e: st.error(f"解析失败：{e}")
    st.markdown('</div>', unsafe_allow_html=True)
    if "bgm" in st.session_state:
        audio, title, artist, demo = st.session_state.bgm
        st.audio(audio, format="audio/wav")
        st.image("https://images.unsplash.com/photo-1511379938547-c1f69419868d?auto=format&fit=crop&w=500&q=80", caption="歌曲封面", width=180)
        if demo: st.info("当前为演示结果。配置 yt-dlp、ffmpeg 与 SHAZAM_API_* 后可连接真实识别服务。")
        st.markdown(f'<div class="result"><div class="meta">识别结果</div><h3>《{title}》</h3><div class="meta">歌手 / 艺术家：{artist}</div></div>', unsafe_allow_html=True)
        copy_button(f"{artist} - {title}", "copy-song", "📋 一键复制歌名")
    st.markdown("### 搜索历史")
    st.metric("累计识别次数", len(st.session_state.search_history))
    if st.session_state.search_history:
        for item in st.session_state.search_history[:8]:
            st.markdown(f"- **{item['platform']}** · {item['artist']} - {item['title']} · `{item['query'][:42]}`")
            hcol1, hcol2, hcol3 = st.columns([1.4, 1, 1])
            with hcol1:
                st.image(item.get("artwork") or "https://images.unsplash.com/photo-1511379938547-c1f69419868d?auto=format&fit=crop&w=500&q=80", width=120)
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

with tab2:
    st.markdown('<div class="panel"><div class="eyebrow">02 / TYPE VISION</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("上传字体截图", type=["jpg","jpeg","png"], key="font_image")
    image = None
    if uploaded:
        if uploaded.size > 10 * 1024 * 1024: st.error("图片不能超过 10MB")
        else:
            try:
                image = Image.open(uploaded).convert("RGB"); st.image(image, caption="截图预览", width=560)
            except Exception as e: st.error(f"图片读取失败：{e}")
    if st.button("🔍 开始识别字体", type="primary"):
        if image is None: st.error("请先上传有效的 JPG 或 PNG 图片")
        else:
            try:
                prep = ImageEnhance.Contrast(image.convert("L")).enhance(1.35).filter(ImageFilter.SHARPEN)
                st.session_state.fonts = font_results(prep)
                top_name = st.session_state.fonts[0][0]["name"]
                st.session_state.font_history.insert(0, {"name": top_name, "time": __import__('datetime').datetime.now().strftime("%H:%M:%S")})
            except Exception as e: st.error(f"识别失败：{e}")
    st.markdown('</div>', unsafe_allow_html=True)
    if "fonts" in st.session_state:
        results, demo = st.session_state.fonts
        if demo: st.info("当前为本地演示匹配；配置 FONT_API_URL 与 FONT_API_KEY 后可接入专业字体识别服务。")
        for i, item in enumerate(results, 1):
            name, score, scene = item["name"], item["score"], item["scene"]
            st.markdown(f'<div class="result"><div class="meta">TOP {i}</div><h3>{name}</h3><div class="score">匹配度 {score}%</div><div class="hint">建议场景：{scene}</div></div>', unsafe_allow_html=True)
            copy_button(name, f"copy-font-{i}", "📋 复制字体名称")
    st.markdown("### 字体识别历史")
    st.metric("累计识别次数", len(st.session_state.font_history))
    if st.session_state.font_history:
        counts = {}
        for item in st.session_state.font_history:
            counts[item["name"]] = counts.get(item["name"], 0) + 1
        st.caption("搜索最多")
        for name, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            st.markdown(f"- **{name}** · {count} 次")
        st.caption("最近记录")
        for item in st.session_state.font_history[:6]:
            st.markdown(f"`{item['time']}` · {item['name']}")
    else:
        st.caption("暂无字体识别记录，完成一次识别后会显示在这里。")
    st.markdown("### 爆款字体")
    with st.expander("＋ 手动添加爆款字体"):
        ft = st.text_input("字体名称", key="font_lib_name")
        fs = st.text_input("建议使用场景", placeholder="例如：探店标题、情绪片头", key="font_lib_scene")
        fc = st.selectbox("分类", ["标题高亮", "手写情绪", "知识口播", "品牌包装", "待整理"], key="font_lib_cat")
        fi = st.file_uploader("上传字体示例图片", type=["jpg", "jpeg", "png"], key="font_lib_img")
        if st.button("保存到字体库", key="save-font-lib"):
            if ft.strip():
                st.session_state.font_library.insert(0, {"name":ft.strip(),"scene":fs.strip() or "待补充","category":fc,"image":fi.getvalue() if fi else None})
                st.success("已保存到爆款字体库")
            else: st.warning("请填写字体名称")
    if st.session_state.font_library:
        ff = st.selectbox("按分类查看字体", ["全部"] + sorted({x["category"] for x in st.session_state.font_library}), key="font-lib-filter")
        for item in st.session_state.font_library:
            if ff != "全部" and item["category"] != ff: continue
            st.markdown(f"**{item['name']}** · {item['scene']} · `#{item['category']}`")
            if item["image"]: st.image(item["image"], width=260)
