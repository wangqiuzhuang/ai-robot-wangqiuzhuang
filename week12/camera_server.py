#!/usr/bin/env python3
"""
Week 12: 手机摄像头 Web 服务器
==============================
提供 HTTPS 页面，手机浏览器打开后调用摄像头，
JPEG 帧通过 WebSocket 发送到 WSL Python 后端。

架构:
  手机浏览器 (HTTPS, 调用摄像头)
      │ JPEG 帧 via WebSocket
      ▼
  WSL Python 服务器 (本文件)
      │ OpenCV 解码 / ArUco 识别
      ▼
  OpenCV 显示窗口

使用方式:
  # 1. 启动服务器
  python3 camera_server.py

  # 2. 手机浏览器访问
  https://<wsl-ip>:5000

  # 3. 需要 SSL 证书 (自签名即可)
  #    openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

依赖:
  pip install flask flask-socketio opencv-python numpy
"""

import os
import sys
import base64
import logging
import numpy as np

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    print("⚠️  opencv-python 未安装")

try:
    from flask import Flask, render_template_string
    from flask_socketio import SocketIO, emit
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False
    print("⚠️  flask / flask-socketio 未安装")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── HTML 页面模板 (手机摄像头) ──
CAMERA_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>📷 手机摄像头 - Week 12</title>
<style>
  body { font-family: sans-serif; text-align: center; background: #111; color: #eee; }
  video { width: 100%; max-width: 400px; border-radius: 8px; margin: 10px 0; }
  button { padding: 12px 24px; font-size: 1.1rem; border: none; border-radius: 8px; cursor: pointer; }
  .start { background: #4ecca3; }
  .stop { background: #e94560; }
  #status { margin: 10px; font-size: 0.8rem; color: #888; }
</style>
</head>
<body>
<h2>🤖 Week 12: 手机摄像头</h2>
<video id="video" autoplay playsinline></video>
<canvas id="canvas" style="display:none"></canvas>
<br>
<button class="start" onclick="startCamera()">📸 开始</button>
<button class="stop" onclick="stopCamera()">⏹️ 停止</button>
<div id="status">等待操作...</div>

<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
<script>
const socket = io();
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let stream = null;
let intervalId = null;

async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment', width: 320, height: 240 }
    });
    video.srcObject = stream;
    document.getElementById('status').textContent = '📸 摄像头已启动';
    startCapturing();
  } catch(e) {
    document.getElementById('status').textContent = '❌ ' + e.message;
  }
}

function startCapturing() {
  intervalId = setInterval(() => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);
    const jpeg = canvas.toDataURL('image/jpeg', 0.6);
    socket.emit('frame', { image: jpeg });
  }, 200); // 5 fps
}

function stopCamera() {
  if (stream) { stream.getTracks().forEach(t => t.stop()); }
  if (intervalId) { clearInterval(intervalId); }
  document.getElementById('status').textContent = '⏹️ 已停止';
}

socket.on('result', (data) => {
  document.getElementById('status').textContent =
    `检测到 ${data.markers || 0} 个 ArUco 标记 | ${data.timestamp}`;
});
</script>
</body>
</html>"""

# ── Flask 应用 ──
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

frame_count = 0


@app.route('/')
def index():
    return render_template_string(CAMERA_HTML)


@socketio.on('frame')
def handle_frame(data):
    """处理手机发来的 JPEG 帧"""
    global frame_count
    frame_count += 1

    try:
        # 解码 base64 JPEG
        jpeg_data = data['image'].split(',')[1]
        jpeg_bytes = base64.b64decode(jpeg_data)
        nparr = np.frombuffer(jpeg_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is not None and HAS_CV2:
            # 可选: 在此添加 ArUco 检测
            # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
            # corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict)
            # num_markers = len(corners) if corners else 0

            # 可显示在 WSL 端
            if frame_count % 10 == 0:
                cv2.imshow('Week 12 - Mobile Camera', cv2.resize(frame, (640, 480)))
                cv2.waitKey(1)

                logger.info(f"📷 收到第 {frame_count} 帧, 尺寸={frame.shape}")

        emit('result', {
            'status': 'ok',
            'frame_id': frame_count,
            'timestamp': str(frame_count),
            'markers': 0,  # 如果需要 ArUco 检测则替换
        })

    except Exception as e:
        logger.error(f"处理帧失败: {e}")
        emit('result', {'status': 'error', 'message': str(e)})


def main():
    if not HAS_FLASK:
        print("❌ 请安装: pip install flask flask-socketio")
        sys.exit(1)
    if not HAS_CV2:
        print("⚠️  opencv-python 未安装，图像处理功能不可用")

    print("\n📡 Week 12: 手机摄像头服务器")
    print("=" * 40)
    print("  手机访问: http://<wsl-ip>:5000")
    print("  确保手机和电脑在同一网络")
    print("  或使用 Tailscale 组网")

    socketio.run(app, host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    main()
