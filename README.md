# M3U8 NAS 下载器

[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4%EF%B8%8F-ff69b4)](https://github.com/sponsors/BlueFang)

一键推送 jable.tv 及任何 m3u8 流媒体到 NAS 下载。

---

## 赞助支持

喜欢这个工具？请考虑赞助支持开发！

👉 通过 GitHub Sponsors 赞助 $5 支持持续更新！

---

## 架构

浏览器油猴脚本 → HTTP POST → NAS API 服务 → N_m3u8DL-RE 下载 → NAS 存储

## 飞牛OS 快速部署

```bash
mkdir -p /vol1/docker/m3u8-dl
cd /vol1/docker/m3u8-dl
cat > docker-compose.yml << \"EOF\"
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

管理页面：http://NAS的IP:8899

## 油猴脚本安装

1. 安装 Tampermonkey 浏览器扩展
2. 点击 Tampermonkey → 添加新脚本
3. 把 userscript.js 的内容粘贴进去
4. 修改 NAS_API 地址为你 NAS 的实际 IP
5. 保存

## 使用

1. 打开 jable.tv 任意影片页面
2. 页面右上角出现 NAS下载 按钮
3. 点击 → 自动抓取 m3u8 → 推送到 NAS
4. NAS 后台自动下载到指定目录

## API 接口

POST /api/download - 提交下载任务
GET /api/status/{id} - 查询任务状态
GET /api/tasks - 列出所有任务
GET / - Web 管理页面

## 故障排除

连不上 NAS: 检查防火墙是否放行 8899 端口
下载失败: 检查容器日志 docker logs m3u8-dl
m3u8 获取失败: 确保页面完全加载后再点按钮

---

## 赞助支持

如果你觉得这个工具好用，欢迎赞助支持开发！

👉 通过 GitHub Sponsors 赞助 $5
