# 映禾小助手

面向短视频创作者的 Streamlit 工作台，包含真实 BGM 识别、视频音轨提取和图片字体相似匹配。

## Streamlit Cloud 配置

仓库根目录必须包含：

- `app.py`
- `requirements.txt`
- `packages.txt`

在 Streamlit Cloud 的 **Settings → Secrets** 中填写：

```toml
AUDD_API_TOKEN = "你的 AudD API Token"

# 云端链接解析服务（可选）。配置后，用户粘贴抖音分享页会先由该服务
# 返回可公开下载的媒体地址，再由本应用提取音频并识别歌曲。
MEDIA_RESOLVER_API_URL = "https://你的解析服务.example/resolve"
MEDIA_RESOLVER_API_KEY = "你的解析服务密钥"

# 推荐设置。设置后，团队成员需要输入这个口令才能使用付费识别额度。
APP_ACCESS_CODE = "你自己设置的团队访问口令"

# 可选。留空时使用内置的开源字体相似匹配服务。
# FONT_API_URL = "https://你的字体识别接口"
# FONT_API_KEY = "你的字体接口密钥"
```

兼容旧配置名 `SHAZAM_API_URL` 和 `SHAZAM_API_KEY`，但新部署推荐使用 `AUDD_API_TOKEN`。

## 多人使用方式

部署完成后，把 Streamlit 应用网址和团队访问口令发给成员即可。每个浏览器标签页使用独立会话，上传文件、识别结果和临时历史不会互相混淆。API Token 只保存在 Streamlit Cloud 服务端。

### 云端链接解析服务要求

解析服务需要接受一个 HTTPS `POST` 请求，请求体为：

```json
{"url":"https://v.douyin.com/...","platform":"抖音 Douyin"}
```

响应 JSON 中需要包含一个 HTTPS 媒体地址，字段可以是 `media_url`、`video_url`、`download_url`、`play_url`，或嵌套在 `data`/`result` 中的 `url`。应用拿到该地址后会下载视频、提取音频、标准化音量，再调用 AudD 识别。

抖音开放平台的官方接口需要用户授权，不能保证为任意分享页返回通用 MP4 下载地址。因此这里的解析服务必须是你已购买或确认合规的服务，不要把抖音账号密码或 Cookie 交给第三方。

## 本地运行

```powershell
pip install -r requirements.txt
streamlit run app.py
```

本地处理视频还需要安装 `ffmpeg`。Streamlit Cloud 会根据 `packages.txt` 自动安装。
