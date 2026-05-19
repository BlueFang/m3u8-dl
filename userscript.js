// ==UserScript==
// @name         Jable 一键推送到 NAS 下载
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  自动抓取 jable 的 m3u8 地址，推送到 NAS 下载
// @match        https://jable.tv/videos/*
// @match        https://*.jable.tv/videos/*
// @grant        GM_xmlhttpRequest
// @connect      *
// ==/UserScript==

(function() {
    'use strict';

    // ========== 配置 ==========
    const NAS_API = 'http://192.168.1.100:8899';  // ★ 改成你飞牛 NAS 的 IP
    // ==========================

    // 创建悬浮按钮
    const btn = document.createElement('button');
    btn.textContent = '⬇ NAS下载';
    btn.style.cssText = `
        position: fixed; top: 20px; right: 20px; z-index: 999999;
        padding: 12px 24px; background: linear-gradient(135deg, #ff4757, #ff6b81);
        color: white; border: none; border-radius: 25px; cursor: pointer;
        font-size: 15px; font-weight: bold; box-shadow: 0 4px 15px rgba(255,71,87,0.4);
        transition: all 0.3s; font-family: -apple-system, sans-serif;
    `;
    btn.onmouseover = () => btn.style.transform = 'scale(1.05)';
    btn.onmouseout = () => btn.style.transform = 'scale(1)';
    document.body.appendChild(btn);

    // 从页面源码提取 m3u8
    function getM3u8Url() {
        const html = document.documentElement.innerHTML;
        const matches = html.match(/https?:\/\/[^"'\s\\]+\.m3u8[^"'\s\\]*/g);
        return matches ? matches[0] : null;
    }

    // 获取标题
    function getTitle() {
        const h2 = document.querySelector('.info h2, h2.title, .video-title');
        if (h2) return h2.textContent.trim();
        return document.title.split(/[–\-|]/)[0].trim() || 'video';
    }

    btn.addEventListener('click', function() {
        var m3u8 = getM3u8Url();
        if (!m3u8) {
            showToast('❌ 未找到 m3u8，请等待加载', '#ff4757');
            return;
        }

        var title = getTitle();
        btn.textContent = '⏳ 推送中...';
        btn.disabled = true;

        GM_xmlhttpRequest({
            method: 'POST',
            url: NAS_API + '/api/download',
            headers: { 'Content-Type': 'application/json' },
            data: JSON.stringify({
                m3u8_url: m3u8,
                save_name: title,
                referer: window.location.href
            }),
            onload: function(resp) {
                if (resp.status === 200) {
                    var result = JSON.parse(resp.responseText);
                    showToast('✅ 已推送到NAS: ' + result.save_name, '#2ed573');
                    btn.textContent = '✅ 已推送';
                    btn.style.background = 'linear-gradient(135deg, #2ed573, #7bed9f)';
                    setTimeout(function() {
                        btn.textContent = '⬇ NAS下载';
                        btn.style.background = 'linear-gradient(135deg, #ff4757, #ff6b81)';
                        btn.disabled = false;
                    }, 3000);
                } else {
                    showToast('❌ 推送失败: ' + resp.status, '#ff4757');
                    btn.textContent = '⬇ NAS下载';
                    btn.disabled = false;
                }
            },
            onerror: function() {
                showToast('❌ 无法连接NAS，请检查地址和网络', '#ff4757');
                btn.textContent = '⬇ NAS下载';
                btn.disabled = false;
            }
        });
    });

    // Toast 提示
    function showToast(msg, color) {
        var toast = document.createElement('div');
        toast.textContent = msg;
        toast.style.cssText = `
            position: fixed; top: 80px; right: 20px; z-index: 999999;
            padding: 12px 20px; background: ${color}; color: white;
            border-radius: 8px; font-size: 14px; font-family: -apple-system, sans-serif;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3); animation: slideIn 0.3s;
        `;
        document.body.appendChild(toast);
        setTimeout(function() { toast.remove(); }, 4000);
    }

    // 添加动画
    var style = document.createElement('style');
    style.textContent = '@keyframes slideIn{from{opacity:0;transform:translateX(30px)}to{opacity:1;transform:translateX(0)}}';
    document.head.appendChild(style);

})();
