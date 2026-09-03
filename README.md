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

# 推荐设置。设置后，团队成员需要输入这个口令才能使用付费识别额度。
APP_ACCESS_CODE = "你自己设置的团队访问口令"

# 可选。留空时使用内置的开源字体相似匹配服务。
# FONT_API_URL = "https://你的字体识别接口"
# FONT_API_KEY = "你的字体接口密钥"
```

兼容旧配置名 `SHAZAM_API_URL` 和 `SHAZAM_API_KEY`，但新部署推荐使用 `AUDD_API_TOKEN`。

## 多人使用方式

部署完成后，把 Streamlit 应用网址和团队访问口令发给成员即可。每个浏览器标签页使用独立会话，上传文件、识别结果和临时历史不会互相混淆。API Token 只保存在 Streamlit Cloud 服务端。

## 本地运行

```powershell
pip install -r requirements.txt
streamlit run app.py
```

本地处理视频还需要安装 `ffmpeg`。Streamlit Cloud 会根据 `packages.txt` 自动安装。
