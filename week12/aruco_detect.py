#!/usr/bin/env python3
"""
Week 12: ArUco 标记检测与识别
==============================
实时检测摄像头画面中的 ArUco 标记，显示 ID 和位姿信息。

ArUco 标记:
  - 类似于二维码的方形标记，用于机器人定位和姿态估计
  - 每个标记有唯一 ID (0-49 在 DICT_4X4_50 字典中)
  - OpenCV 内置了完整的 ArUco 检测流程

核心流程:
  1. 从摄像头/视频流读取帧
  2. 检测 ArUco 标记 → 获取角点 + ID
  3. 估计标记的 3D 位姿 (需要相机内参)
  4. 在图像上绘制标记边框和 ID

运行方式:
  pip install opencv-contrib-python numpy
  python3 aruco_detect.py                    # 使用默认摄像头
  python3 aruco_detect.py --image test.jpg   # 检测图片中的标记
  python3 aruco_detect.py --camera 1         # 使用指定摄像头
"""

import sys
import argparse
import numpy as np

try:
    import cv2
    from cv2 import aruco
except ImportError:
    print("❌ opencv-contrib-python 未安装!")
    print("   pip install opencv-contrib-python")
    sys.exit(1)


class ArUcoDetector:
    """ArUco 标记检测器"""

    # ArUco 字典选项
    DICT_OPTIONS = {
        '4x4': aruco.DICT_4X4_50,
        '5x5': aruco.DICT_5X5_50,
        '6x6': aruco.DICT_6X6_50,
        '7x7': aruco.DICT_7X7_50,
    }

    def __init__(self, dict_type='4x4', camera_id=0):
        """初始化检测器"""
        self.dict_type = dict_type
        self.aruco_dict = aruco.getPredefinedDictionary(self.DICT_OPTIONS[dict_type])
        self.parameters = aruco.DetectorParameters()

        # 相机设置
        self.camera_id = camera_id
        self.cap = None

        # 检测历史
        self.detection_history = []
        self.max_history = 10

        print(f"🔍 ArUco 检测器初始化: 字典={dict_type}")

    def start_camera(self):
        """打开摄像头"""
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise RuntimeError(f"无法打开摄像头 {self.camera_id}")
        print(f"📷 摄像头 {self.camera_id} 已打开")

    def detect_frame(self, frame: np.ndarray) -> dict:
        """
        检测单帧中的所有 ArUco 标记

        返回:
          {
            'ids':          [[id1], [id2], ...],  # 检测到的标记ID
            'corners':      [corners1, corners2, ...],  # 四个角点坐标
            'num_markers':  int,  # 检测到的标记数量
          }
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = aruco.detectMarkers(
            gray, self.aruco_dict, parameters=self.parameters
        )

        result = {
            'ids': ids,
            'corners': corners,
            'num_markers': len(corners) if corners else 0,
        }

        self.detection_history.append(result)
        if len(self.detection_history) > self.max_history:
            self.detection_history.pop(0)

        return result

    def draw_detections(self, frame: np.ndarray, detection: dict) -> np.ndarray:
        """在图像上绘制检测结果"""
        if detection['corners']:
            frame = aruco.drawDetectedMarkers(
                frame, detection['corners'], detection['ids'],
                borderColor=(0, 255, 0)
            )

        # 叠加信息面板
        h, w = frame.shape[:2]

        # 半透明面板
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (300, 100), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)

        # 检测信息
        cv2.putText(frame, f"ArUco Detection ({self.dict_type})",
                    (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Markers: {detection['num_markers']}",
                    (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 0) if detection['num_markers'] > 0 else (0, 0, 255), 2)

        if detection['ids'] is not None:
            ids_str = ', '.join(str(id_[0]) for id_ in detection['ids'])
            cv2.putText(frame, f"IDs: {ids_str}",
                        (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

        return frame

    def run_realtime(self):
        """实时检测循环"""
        self.start_camera()

        print("\n🎥 实时检测中... 按 'q' 退出, 按 's' 截图")
        print("   将 ArUco 标记对准摄像头")

        frame_count = 0

        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("⚠️  读取帧失败")
                    break

                # 检测
                detection = self.detect_frame(frame)

                # 绘制
                display = self.draw_detections(frame, detection)

                # 显示
                cv2.imshow('ArUco Detection - Week 12', display)

                frame_count += 1
                if frame_count % 30 == 0:  # 每 30 帧输出一次
                    print(f"  帧 {frame_count}: 检测到 {detection['num_markers']} 个标记")

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    cv2.imwrite(f'aruco_detect_{frame_count}.jpg', display)
                    print(f"  💾 已截图: aruco_detect_{frame_count}.jpg")

        except KeyboardInterrupt:
            pass
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            print(f"🛑 检测结束，共处理 {frame_count} 帧")

    def detect_image(self, image_path: str):
        """检测单张图片中的 ArUco 标记"""
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"❌ 无法读取图片: {image_path}")
            return

        detection = self.detect_frame(frame)
        display = self.draw_detections(frame, detection)

        # 保存结果
        output_path = image_path.replace('.', '_detected.')
        cv2.imwrite(output_path, display)

        print(f"📷 检测完成:")
        print(f"   图片:    {image_path}")
        print(f"   标记数:  {detection['num_markers']}")
        if detection['ids'] is not None:
            for i, id_ in enumerate(detection['ids']):
                corners = detection['corners'][i][0]
                center = corners.mean(axis=0)
                print(f"   标记 {id_[0]}: 中心=({center[0]:.0f}, {center[1]:.0f})")
        print(f"   结果:    {output_path}")


def main():
    parser = argparse.ArgumentParser(description='ArUco 标记检测')
    parser.add_argument('--image', type=str, help='检测单张图片')
    parser.add_argument('--camera', type=int, default=0, help='摄像头ID (默认0)')
    parser.add_argument('--dict', type=str, default='4x4',
                        choices=['4x4', '5x5', '6x6', '7x7'],
                        help='ArUco 字典类型 (默认4x4)')
    args = parser.parse_args()

    detector = ArUcoDetector(dict_type=args.dict, camera_id=args.camera)

    if args.image:
        detector.detect_image(args.image)
    else:
        detector.run_realtime()


if __name__ == '__main__':
    main()
