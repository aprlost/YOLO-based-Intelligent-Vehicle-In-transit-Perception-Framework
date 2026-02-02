# YOLO-based-Intelligent-Vehicle-In-transit-Perception-Framework

# 基于 YOLO 的智能车在途感知框架
# YOLO-based Intelligent Vehicle In-transit Perception Framework

<div align="center">

<img src="https://via.placeholder.com/150?text=Vehicle+Perception" height="120" alt="Logo"/>

<br>

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-1.10%2B-orange)
![YOLOv5](https://img.shields.io/badge/Model-YOLOv5-green)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-red)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

**一个集成了计算机视觉与多源传感器融合的智能车载感知系统。**
<br>
利用 **YOLOv5** 进行实时目标检测，结合 **GNSS/IMU** 串口通信实现车辆状态的全方位感知。

[功能特性](#-功能特性) • [安装指南](#-安装指南) • [使用说明](#-使用说明) • [效果展示](#-效果展示)

</div>

---

## 📖 项目简介 (Introduction)

本项目旨在解决智能交通系统中车辆对周界环境感知的不确定性问题。系统基于 Python 开发，通过软硬件协同，实现了以下核心能力：

1.  **视觉感知**：利用 YOLOv5 深度学习算法，对车载摄像头视频流中的“行人”和“车辆”进行实时识别与计数。
2.  **多源信息融合**：通过串口通信（Serial）解析 NMEA-0183 协议，实时获取并显示车辆的经纬度、速度、海拔、航向及卫星状态。
3.  **交互式终端**：基于 PyQt5 设计了可视化 GUI，支持视频录制、截图保存以及各类传感器数据的实时仪表盘显示。

## ✨ 功能特性 (Features)

* **🔍 实时目标检测**：
    * 集成 YOLOv5 模型，支持 Webcam 或视频流输入。
    * 实时统计画面中的 **车辆 (Car)** 和 **行人 (Person)** 数量。
* **📡 GNSS 数据解析**：
    * 支持 `$GPGGA` 和 `$GPRMC` 语句解析。
    * 实时显示：经纬度（自动判断半球）、地面速度 (km/h)、UTC时间转北京时间、卫星数量。
* **🖥️ 现代化 GUI 界面**：
    * 实时视频回传显示。
    * 大字体仪表盘数据显示（速度、时间、计数）。
    * 包含 **截图 (Screenshot)** 和 **录像 (Screen Recording)** 功能。
* **💾 数据记录**：
    * 支持检测结果的视频保存 (.avi/.mp4)。
    * 支持关键帧截图保存。

## 📸 效果展示 (Demo)

> *建议：在此处上传实际运行的 GUI 截图，展示左侧视频检测与右侧数据面板。*

<div align="center">
    <img src="https://via.placeholder.com/800x450?text=Please+Upload+Your+GUI+Screenshot+Here" width="800" alt="System GUI">
</div>

## 🛠️ 安装指南 (Installation)

### 1. 克隆仓库
```bash
git clone [https://github.com/aprlost/YOLO-based-Intelligent-Vehicle-In-transit-Perception-Framework.git](https://github.com/aprlost/YOLO-based-Intelligent-Vehicle-In-transit-Perception-Framework.git)
cd YOLO-based-Intelligent-Vehicle-In-transit-Perception-Framework
