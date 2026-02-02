
# 基于 YOLO 的智能车在途感知框架

<div align="center">
<br>

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-1.10%2B-orange)
![YOLOv5](https://img.shields.io/badge/Model-YOLOv5-green)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-red)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

**一个集成了CV与传感器融合的智能车载感知框架——利用 **YOLOv5** 进行实时目标检测，结合 **GNSS/IMU** 串口通信实现车辆状态的全方位感知。**
<br>
</div>

---

主要工作内容：标注并训练人车数据集，基于 **YOLO** 实现视频流目标的识别与计数；开发 **Qt** 界面与串口程序解析 **GNSS/IMU** 数据，实时解算并显示人车定位状态。
本项目旨在解决智能交通系统中车辆对周界环境感知的不确定性问题。系统基于 Python和Pytorch 开发，通过软硬件协同，实现了以下核心能力：

1.  **视觉感知**：利用 YOLOv5 深度学习算法，对车载摄像头视频流中的“行人”和“车辆”进行实时识别与计数。
2.  **多源信息融合**：通过串口通信解析 NMEA-0183 协议，实时获取并显示车辆的经纬度、速度、海拔、航向及卫星状态。
3.  **交互式终端**：基于 PyQt5 设计了可视化 GUI，支持视频录制、截图保存以及各类传感器数据的实时仪表盘显示。


* **实时目标检测**：
    * 集成 YOLOv5 模型，支持 Webcam 或视频流输入。
    * 实时统计画面中的 **车辆 (Car)** 和 **行人 (Person)** 数量。
* **GNSS 数据解析**：
    * 支持 `$GPGGA` 和 `$GPRMC` 语句解析。
    * 实时显示：经纬度、地面速度、UTC时间转北京时间、卫星数量。
* **现代化 GUI 界面**：
    * 实时视频回传显示。
    * 仪表盘数据显示。
    * 包含 **截图** 和 **录像** 功能。
* **数据记录**：
    * 支持检测结果的视频保存。
    * 支持关键帧截图保存。

## 📸 效果展示 (Demo)

<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="./assets/demo1.gif" width="400" alt="场景1"/>
        <br>
        <sub><b>场景 1</b></sub>
      </td>
      <td align="center">
        <img src="./assets/demo2.gif" width="400" alt="场景2"/>
        <br>
        <sub><b>场景 2</b></sub>
      </td>
    </tr>
    <tr>
      <td align="center">
        <img src="./assets/demo3.gif" width="400" alt="场景3"/>
        <br>
        <sub><b>场景 3</b></sub>
      </td>
      <td align="center">
        <img src="./assets/demo4.gif" width="400" alt="场景4"/>
        <br>
        <sub><b>场景 4</b></sub>
      </td>
    </tr>
  </table>
</div>


### 1. 克隆仓库
```bash
git clone [https://github.com/aprlost/YOLO-based-Intelligent-Vehicle-In-transit-Perception-Framework.git](https://github.com/aprlost/YOLO-based-Intelligent-Vehicle-In-transit-Perception-Framework.git)
cd YOLO-based-Intelligent-Vehicle-In-transit-Perception-Framework
```
### 2.  环境配置
建议使用 Conda 创建独立环境以避免依赖冲突：
```
conda create -n vehicle-perception python=3.8
conda activate vehicle-perception
```
### 3. 安装依赖
本项目依赖 YOLOv5 的基础环境以及 PyQt5 和 串口通信库。请确保安装以下核心库，以及代码内其他相关库等：
```
pip install PyQt5 pyserial pynmea2 pyautogui opencv-python torch torchvision
```

### 4. 硬件连接
摄像头：确保 USB 摄像头已连接。

GNSS 模块：连接电脑。

注意：默认串口号配置为 COM16。如果你的设备端口不同，请务必打开 final.py 修改以下代码：
```
ser = serial.Serial(port="COM16", baudrate=115200, ...)
```
### 5. 运行系统
直接运行主程序即可启动 Qt 界面：
```
python final.py
```
### 6. 操作指南
显示视频：点击界面上的“显示视频”按钮，加载 YOLO 模型并开始推理。

显示文本：点击“显示文本”按钮，开始读取并解析串口 GPS 数据。

功能按钮：

截图：保存当前界面截图到本地。
录像：点击开始录制，再次点击停止录制（保存在项目根目录）。


