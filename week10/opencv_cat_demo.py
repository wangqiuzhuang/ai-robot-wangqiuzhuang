#!/usr/bin/env python3
"""
Week 10: Docker 容器中的 OpenCV 图像处理实验
============================================
在 Docker 容器内运行的 OpenCV 图像处理演示程序。

功能:
  1. 读取图片 → 颜色空间转换 (RGB → HSV → Gray)
  2. 边缘检测 (Canny)
  3. 图像滤波 (高斯模糊)
  4. 结果拼接并显示

依赖:
  pip install opencv-python numpy

运行方式:
  python3 opencv_cat_demo.py [图片路径]
  # 默认使用当前目录下的 cat.jpg
"""

import sys
import os
import numpy as np

try:
    import cv2
except ImportError:
    print("❌ opencv-python 未安装! 请执行: pip install opencv-python")
    sys.exit(1)


def load_image(path: str) -> np.ndarray:
    """加载图像，支持默认猫图"""
    if os.path.exists(path):
        return cv2.imread(path)

    print(f"⚠️  图片不存在: {path}")
    print("   生成测试图像...")

    # 生成一个彩色测试图案
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    # 彩虹条纹
    for i in range(7):
        y_start = i * 57
        y_end = (i + 1) * 57
        color = [
            (0, 0, 255),    # 红
            (0, 127, 255),  # 橙
            (0, 255, 255),  # 黄
            (0, 255, 0),    # 绿
            (255, 0, 0),    # 蓝
            (130, 0, 75),   # 靛
            (255, 0, 255),  # 紫
        ][i]
        cv2.rectangle(img, (0, y_start), (600, y_end), color, -1)
    # 画圆形
    cv2.circle(img, (300, 200), 100, (255, 255, 255), 3)
    cv2.putText(img, 'OpenCV Demo', (180, 210),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    return img


def color_space_demo(img: np.ndarray) -> dict:
    """
    颜色空间转换演示
    RGB → HSV → Gray
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return {'HSV': hsv, 'Gray': gray}


def edge_detection_demo(img: np.ndarray) -> dict:
    """
    边缘检测对比
    Canny (双阈值) vs Sobel
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Canny 边缘检测
    canny = cv2.Canny(gray, 50, 150)

    # Sobel 边缘检测
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    sobel = cv2.magnitude(sobel_x, sobel_y)
    sobel = np.uint8(np.clip(sobel, 0, 255))

    return {'Canny': canny, 'Sobel': sobel}


def filter_demo(img: np.ndarray) -> dict:
    """
    图像滤波对比
    Gaussian (高斯模糊) vs Median (中值滤波) vs Bilateral (双边滤波)
    """
    gaussian = cv2.GaussianBlur(img, (7, 7), 0)
    median = cv2.medianBlur(img, 7)
    bilateral = cv2.bilateralFilter(img, 9, 75, 75)

    return {
        'Gaussian Blur': gaussian,
        'Median Blur': median,
        'Bilateral Filter': bilateral
    }


def create_display_grid(images: dict, labels: list, grid_shape: tuple,
                         cell_size=(320, 240)) -> np.ndarray:
    """创建结果展示网格"""
    rows, cols = grid_shape
    h, w = cell_size
    canvas = np.zeros((h * rows, w * cols, 3), dtype=np.uint8)

    for idx, label in enumerate(labels):
        if idx >= rows * cols:
            break
        r, c = idx // cols, idx % cols
        img = images.get(label)

        if img is not None:
            # 确保是 3 通道
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            # 缩放
            img_resized = cv2.resize(img, (w, h))
            # 添加标签
            cv2.putText(img_resized, label, (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            canvas[r * h:(r + 1) * h, c * w:(c + 1) * w] = img_resized

    return canvas


def main():
    # 加载图片
    image_path = sys.argv[1] if len(sys.argv) > 1 else 'cat.jpg'
    print(f"🐱 Week 10: OpenCV 图像处理演示")
    print(f"   图片: {image_path}")
    img = load_image(image_path)
    print(f"   尺寸: {img.shape[1]}x{img.shape[0]}")

    # 颜色空间转换
    print("\n🎨 颜色空间转换...")
    color_results = color_space_demo(img)

    # 边缘检测
    print("📐 边缘检测...")
    edge_results = edge_detection_demo(img)

    # 滤波对比
    print("🔍 图像滤波...")
    filter_results = filter_demo(img)

    # 拼接显示
    print("\n📊 生成结果展示...")
    all_results = {
        'Original': img,
        **color_results,
        **edge_results,
        **filter_results,
    }

    display = create_display_grid(
        all_results,
        ['Original', 'HSV', 'Gray', 'Canny', 'Sobel',
         'Gaussian Blur', 'Median Blur', 'Bilateral Filter'],
        grid_shape=(2, 4),
        cell_size=(300, 200)
    )

    # 保存结果
    output_path = 'opencv_results.png'
    cv2.imwrite(output_path, display)
    print(f"💾 结果已保存: {output_path}")

    # 统计信息
    print(f"\n📊 图像统计:")
    print(f"   均值 (BGR):     {img.mean(axis=(0,1)).astype(int)}")
    print(f"   标准差 (BGR):   {img.std(axis=(0,1)).astype(int)}")
    print(f"   边缘像素占比:    {np.mean(edge_results['Canny'] > 0) * 100:.1f}%")

    print("\n✅ 图像处理完成!")


if __name__ == '__main__':
    main()
