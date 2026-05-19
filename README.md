# M3U8 NAS 下载器

一键推送 jable.tv（及任何 m3u8 流媒体）到 NAS 下载。

## 架构

```
浏览器（油猴脚本） → HTTP POST → NAS（API 服务） → N_m3u8DL-RE 下载 → NAS 存储
```

## 飞牛OS 快速部署

```bash
mkdir -p /vol1/docker/m3u8-dl && cd /vol1/docker/m3u8-dl

cat > docker-compose.yml << 'EOF'
services:
  m3u8-dl:
    image: bluefang/m3u8-dl:latest
    container_name: m3u8-dl
    ports:
      - "8899:8899"
    volumes:
      - /vol1/downloads:/downloads
    environment:
      - TZ=Asia/Shanghai
    restart: unless-stopped
EOF

docker compose up -d
```

管理页面：`http://NAS的IP:8899`

## 油猴脚本安装

1. 安装 [Tampermonkey](https://www.tampermonkey.net/) 浏览器扩展
2. 点击 Tampermonkey → 添加新脚本
3. 把 `userscript.js` 的内容粘贴进去
4. **重要：修改 `NAS_API` 地址为你 NAS 的实际 IP**
5. 保存

## 使用

1. 打开 jable.tv 任意影片页面
2. 页面右上角出现「⬇ NAS下载」按钮
3. 点击 → 自动抓取 m3u8 → 推送到 NAS
4. NAS 后台自动下载到指定目录

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/download` | 提交下载任务 |
| GET | `/api/status/{id}` | 查询任务状态 |
| GET | `/api/tasks` | 列出所有任务 |
| GET | `/` | Web 管理页面 |

### 提交下载示例

```bash
curl -X POST http://NAS:8899/api/download \
  -H "Content-Type: application/json" \
  -d '{"m3u8_url":"https://xxx.m3u8","save_name":"我的视频"}'
```

## 本地构建（不走 Docker Hub）

```bash
cd /vol1/docker/m3u8-dl
docker compose -f docker-compose.local.yml up -d --build
```

## 发布到 Docker Hub（开发者）

1. Fork 本仓库到 `bluefang` 账号
2. 在 GitHub 仓库 Settings → Secrets 中添加：
   - `DOCKERHUB_USERNAME` = `bluefang`
   - `DOCKERHUB_TOKEN` = Docker Hub Access Token（在 hub.docker.com → Account Settings → Security 创建）
3. 打 tag 触发自动构建：
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
4. 或者在 GitHub Actions 页面手动触发 workflow_dispatch
5. 构建完成后镜像地址：`bluefang/m3u8-dl:latest`

## 故障排除

- **连不上 NAS**: 检查防火墙是否放行 8899 端口
- **下载失败**: 检查容器日志 `docker logs m3u8-dl`
- **m3u8 获取失败**: 确保页面完全加载后再点按钮
