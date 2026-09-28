# Subtitle Collage

本地 Web 版影视字幕截图自动拼贴工具 MVP。

## 功能

- 多图上传、原图预览、拖拽排序、删除图片
- 在预览图上调整底部字幕高度，并按比例应用到全部截图
- 批量裁剪非封面图片的字幕条
- 选择图片是否参与导出
- 选择顶部完整截图，生成 PNG/JPG 长图并预览下载
- 自动恢复上次打开的本地项目

## 后端启动

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

后端地址：`http://127.0.0.1:8000`  
Swagger：`http://127.0.0.1:8000/docs`

## 前端启动

```powershell
cd frontend
npm install
npm run dev
```

前端地址：`http://127.0.0.1:5173`

## 纯 Python 演示

```powershell
cd backend
python run_demo.py --input ../samples --cover ../samples/001.png --roi 0.0,0.72,1.0,0.25 --output ../output/collage.png
```

## 打包 Windows exe

```powershell
cd E:\code\project
.\build_exe.ps1
```

产物位置：

```text
release/SubtitleCollage/SubtitleCollage.exe
```

双击 exe 后会启动本地服务并自动打开浏览器。用户数据保存在 exe 同级目录下的 `data/`。
