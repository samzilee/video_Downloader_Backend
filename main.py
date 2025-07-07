from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from yt_dlp import YoutubeDL

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://video-downloader-samzi.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/download")
async def get_all_video_formats(request: Request):
    data = await request.json()
    video_url = data.get("url")

    if not video_url:
        raise HTTPException(status_code=400, detail="No URL provided")

    ydl_opts = {
        "quiet": True,
        # "cookiefile": "cookies.txt",  # optional
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            formats = []
            for fmt in info.get("formats", []):
                # Filter out audio-only or dash fragments if you want
                # if fmt.get("vcodec") != "none" and fmt.get("acodec") != "none":
                formats.append({
                    "format_id": fmt.get("format_id"),
                    "ext": fmt.get("ext"),
                    "resolution": f"{fmt.get('height')}p" if fmt.get("height") else "audio",
                    "filesize": fmt.get("filesize"),
                    "url": fmt.get("url"),
                    "fps": fmt.get("fps"),
                    "video_codec": fmt.get("vcodec"),
                    "audio_codec": fmt.get("acodec"),
                })

            return {
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "duration": info.get("duration"),  # in seconds
                "uploader": info.get("uploader"),
                "formats": formats,
            }

    except Exception as e:
        print("yt-dlp error:", e)
        raise HTTPException(status_code=500, detail="Failed to extract formats")
