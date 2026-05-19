from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import subprocess
import os
import datetime
import threading

app = FastAPI(title="M3U8 下载服务")

DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "/downloads")
TOOL_BIN = os.environ.get("TOOL_BIN", "/usr/local/bin/N_m3u8DL-RE")

tasks = {}
tasks_lock = threading.Lock()


class DownloadRequest(BaseModel):
    m3u8_url: str
    save_name: str = ""
    referer: str = ""
    user_agent: str = ""


def do_download(task_id, m3u8_url, save_name, referer, user_agent):
    with tasks_lock:
        tasks[task_id]["status"] = "downloading"

    cmd = [
        TOOL_BIN, m3u8_url,
        "--save-dir", DOWNLOAD_DIR,
        "--save-name", save_name,
        "--auto-select",
        "--binary-merge",
        "--log-level", "info",
    ]
    if referer:
        cmd += ["--referer", referer]
    if user_agent:
        cmd += ["--user-agent", user_agent]
    else:
        cmd += ["--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
        with tasks_lock:
            tasks[task_id]["status"] = "done" if result.returncode == 0 else "failed"
            tasks[task_id]["log"] = (result.stdout + "\n" + result.stderr)[-1000:]
    except subprocess.TimeoutExpired:
        with tasks_lock:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["log"] = "下载超时（2小时）"
    except Exception as e:
        with tasks_lock:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["log"] = str(e)


@app.post("/api/download")
async def download(req: DownloadRequest, bg: BackgroundTasks):
    if not req.m3u8_url:
        raise HTTPException(400, "m3u8_url 不能为空")

    task_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    save_name = req.save_name or req.m3u8_url.split("/")[-1].replace(".m3u8", "").split("?")[0]
    save_name = save_name.replace("/", "_").replace("\\", "_").replace(":", "_")

    with tasks_lock:
        tasks[task_id] = {
            "url": req.m3u8_url,
            "save_name": save_name,
            "status": "queued",
            "created": task_id[:15],
        }

    bg.add_task(do_download, task_id, req.m3u8_url, save_name, req.referer, req.user_agent)
    return {"task_id": task_id, "save_name": save_name, "status": "queued"}


@app.get("/api/status/{task_id}")
async def get_status(task_id):
    with tasks_lock:
        t = tasks.get(task_id)
    if not t:
        raise HTTPException(404, "任务不存在")
    return t


@app.get("/api/tasks")
async def list_tasks():
    with tasks_lock:
        return tasks


@app.get("/", response_class=HTMLResponse)
async def index():
    with tasks_lock:
        rows = ""
        for tid, t in sorted(tasks.items(), reverse=True):
            sc = {"queued":"#ffa502","downloading":"#1e90ff","done":"#2ed573","failed":"#ff4757"}.get(t["status"],"#888")
            rows += f'<tr><td>{t.get("created",tid[:15])}</td><td title="{t["url"]}">{t.get("save_name","?")}</td><td><span style="color:{sc};font-weight:bold">{t["status"]}</span></td></tr>'

    return f"""<html><head><title>M3U8 下载管理</title>
<style>body{{font-family:-apple-system,sans-serif;max-width:900px;margin:40px auto;padding:0 20px;background:#1a1a2e;color:#eee}}
h1{{color:#ff6b81}}table{{width:100%;border-collapse:collapse;margin-top:20px}}
th,td{{padding:10px;text-align:left;border-bottom:1px solid #333}}th{{color:#ff6b81}}
input,button{{padding:8px 12px;margin:4px;border-radius:6px;border:1px solid #444;background:#16213e;color:#eee}}
button{{background:#ff4757;cursor:pointer;border:none;font-weight:bold}}
button:hover{{background:#ff6b81}}
#result{{margin-top:10px;padding:10px;border-radius:6px;display:none}}</style></head>
<body><h1>M3U8 下载管理器</h1>
<div><input id="url" placeholder="粘贴 m3u8 地址..." style="width:60%">
<input id="name" placeholder="文件名（可选）" style="width:20%">
<button onclick="submit()">下载</button></div><div id="result"></div>
<h2>任务列表</h2><table><tr><th>时间</th><th>文件名</th><th>状态</th></tr>{rows}</table>
<script>async function submit(){{var u=document.getElementById('url').value,n=document.getElementById('name').value,r=document.getElementById('result');
if(!u){{r.style.display='block';r.innerHTML='请输入 m3u8 地址';return}}
try{{var resp=await fetch('/api/download',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{m3u8_url:u,save_name:n}})}});
var d=await resp.json();r.style.display='block';r.style.background='#16213e';r.innerHTML='任务已创建: '+d.task_id+' → '+d.save_name;setTimeout(()=>location.reload(),1000)}}
catch(e){{r.style.display='block';r.innerHTML='请求失败: '+e}}}}
setTimeout(()=>location.reload(),15000)</script></body></html>"""
