FROM python:3.11-slim
WORKDIR /app

# 安装 N_m3u8DL-RE（Linux x64 版本）
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 下载最新版 N_m3u8DL-RE v0.5.1-beta
RUN curl -L -o /tmp/nm3u8.tar.gz \
    "https://github.com/nilaoda/N_m3u8DL-RE/releases/download/v0.5.1-beta/N_m3u8DL-RE_v0.5.1-beta_linux-x64_20251029.tar.gz" \
    && tar -xzf /tmp/nm3u8.tar.gz -C /usr/local/bin/ \
    && chmod +x /usr/local/bin/N_m3u8DL-RE* \
    && rm /tmp/nm3u8.tar.gz

# 安装 Python 依赖
RUN pip install --no-cache-dir fastapi uvicorn

COPY server.py .

EXPOSE 8899
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8899"]
