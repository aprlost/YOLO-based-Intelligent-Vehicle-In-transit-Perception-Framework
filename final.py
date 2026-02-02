# ==========================================
# 模块导入部分
# ==========================================
import sys  # 导入系统模块，用于处理命令行参数、系统路径等
import cv2  # 导入OpenCV库，用于图像处理、视频流读取和保存
import pynmea2  # 导入NMEA协议解析库，用于处理GPS数据
from PyQt5.QtGui import *  # 导入PyQt5的GUI相关模块（字体、图标、图像等）
from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QGraphicsPixmapItem  # 导入具体的窗口控件
from PyQt5 import QtCore, QtGui, QtWidgets  # 导入PyQt5的核心模块
from PyQt5.QtWidgets import QApplication, QLabel, QAction, qApp, QFileDialog  # 导入常用控件
from PyQt5.QtGui import QPixmap  # 导入用于处理图像显示的类
from sys import argv, exit  # 从sys导入特定函数
from PyQt5 import QtCore, QtWidgets  # 重复导入，保留原样
import serial.tools.list_ports  # 导入串口工具，用于列出可用串口
import numpy as np  # 导入NumPy库，用于矩阵运算和图像数组处理
import pyautogui  # 导入屏幕截图库
import GNSS  # 自定义模块（原代码中可能未实际使用或被注释）
import serial  # 导入pyserial库，用于串口通信
import detect  # 导入YOLOv5的检测模块
import sys  # 重复导入
import cv2  # 重复导入
# ... (以下几行均为重复导入，实际开发中应清理，这里为了保持原样保留)
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QGraphicsPixmapItem
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QLabel, QAction, qApp, QFileDialog
from PyQt5.QtGui import QPixmap
from sys import argv, exit
from PyQt5 import QtCore, QtWidgets
import serial.tools.list_ports
import numpy as np
import pyautogui
# import GNSS
import serial
import detect
import argparse  # 用于解析命令行参数
import csv  # 用于读写CSV文件
import os  # 用于操作系统交互（路径、文件检查）
import platform  # 用于获取操作系统信息
import sys
from pathlib import Path  # 用于面向对象的文件路径操作

import torch  # 导入PyTorch深度学习框架

# ==========================================
# YOLOv5 路径初始化
# ==========================================
FILE = Path(__file__).resolve()  # 获取当前脚本的绝对路径
ROOT = FILE.parents[0]  # 获取当前脚本的父目录，作为YOLOv5的根目录
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # 将YOLOv5根目录加入系统环境变量，以便能导入models和utils下的模块
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # 将路径转换为相对路径

# 导入YOLOv5工具库
from ultralytics.utils.plotting import Annotator, colors, save_one_box  # 用于画框、颜色生成

# 导入YOLOv5模型加载器
from models.common import DetectMultiBackend
# 导入数据加载器（支持图片、视频、截图、流媒体）
from utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages, LoadScreenshots, LoadStreams
# 导入通用的工具函数
from utils.general import (
    LOGGER,  # 日志记录器
    Profile,  # 性能分析工具
    check_file,  # 检查文件是否存在
    check_img_size,  # 检查并调整图片尺寸以符合模型步长
    check_imshow,  # 检查环境是否支持显示图片
    check_requirements,  # 检查依赖包
    colorstr,  # 字符串颜色处理
    cv2,
    increment_path,  # 自动递增文件路径（如 exp1, exp2...）
    non_max_suppression,  # 非极大值抑制（NMS），核心算法，用于去除重复框
    print_args,  # 打印参数
    scale_boxes,  # 将预测框坐标从缩放后的尺寸还原回原图尺寸
    strip_optimizer,  # 移除模型中的优化器以减小模型体积
    xyxy2xywh,  # 坐标格式转换（左上角XY+右下角XY -> 中心XY+宽高）
)
from utils.torch_utils import select_device, smart_inference_mode  # 设备选择（CPU/GPU）和推理模式装饰器


# ==========================================
# GPS 数据处理辅助函数
# ==========================================

def DaysOfTheMonth(year, month):
    """
    功能：根据年份和月份，返回该月有多少天。
    原理：处理闰年逻辑（能被4整除且不能被100整除，或能被400整除...）。
    """
    Feb = 28
    # 闰年判断逻辑
    if year % 4 == 0 and year % 100 != 0:
        Feb = 29
    elif year % 400 == 0:
        Feb = 29
    elif year % 3200 == 0 and year % 172800 == 0:
        Feb = 29

    # 对应月份天数映射
    if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
        return 31
    elif month == 4 or month == 6 or month == 9 or month == 11:
        return 30
    else:
        return Feb  # 返回二月天数


def UTCtoG8(UTC_time, UTC_date):
    """
    功能：将UTC时间（世界协调时）转换为东八区时间（北京时间）。
    原理：小时+8，如果超过24则天数+1，天数超过当月最大天数则月份+1，以此类推。
    """
    hour = UTC_time.hour
    minute = UTC_time.minute
    second = UTC_time.second
    year = UTC_date.year
    month = UTC_date.month
    day = UTC_date.day

    hour = hour + 8  # 东八区加8小时
    if hour > 23:  # 跨天处理
        hour = hour - 24
        day = day + 1

    # 跨月处理
    if day > DaysOfTheMonth(year, month):
        day = day - DaysOfTheMonth(year, month)
        month = month + 1

    # 跨年处理
    if month > 12:
        year = year + 1
        month = month - 12

    return year, month, day, hour, minute, second


def position_get(GPGGA, GPRMC):
    """
    功能：解析原始的NMEA 0183协议数据。
    输入：$GPGGA语句（定位数据）和$GPRMC语句（推荐最小数据）。
    输出：解析后的状态、时间、经纬度、速度、航向等信息。
    """
    GGA = pynmea2.parse(GPGGA)  # 使用库解析GPGGA
    RMC = pynmea2.parse(GPRMC)  # 使用库解析GPRMC

    loc_status = RMC.status  # 定位状态 (A=有效, V=无效)
    loc_mode = RMC.mode_indicator  # 定位模式 (A=自主, D=差分...)
    date_UTC = RMC.datestamp  # UTC日期对象
    time_UTC = RMC.timestamp  # UTC时间对象
    longitude = RMC.longitude  # 经度（浮点数）
    latitude = RMC.latitude  # 纬度（浮点数）
    longitude_hemisphere = RMC.lon_dir  # 经度方向 (E/W)
    latitude_hemisphere = RMC.lat_dir  # 纬度方向 (N/S)
    velocity = RMC.spd_over_grnd * 1.852  # 速度转换：1节(knot) = 1.852 km/h
    altitude = GGA.altitude  # 海拔高度
    direction = RMC.true_course  # 真北航向
    gsv = GGA.num_sats  # 卫星数量

    # 调用时间转换函数
    year, month, day, hour, minute, second = UTCtoG8(time_UTC, date_UTC)

    # 中文化方向
    if longitude_hemisphere == 'W':
        longitude_hemisphere = '西经'
    elif longitude_hemisphere == 'E':
        longitude_hemisphere = '东经'
    if latitude_hemisphere == 'N':
        latitude_hemisphere = '北纬'
    elif latitude_hemisphere == 'S':
        latitude_hemisphere = '南纬'

    # 打包标准信息和时间信息
    std_inf = (
        loc_status, loc_mode, date_UTC, time_UTC, longitude, latitude, longitude_hemisphere, latitude_hemisphere,
        velocity,
        altitude, direction)
    G8_time = (year, month, day, hour, minute, second)

    return std_inf, G8_time, gsv


def print_result(res):
    """
    功能：将解析后的GPS数据格式化为可读的字符串，用于在GUI上显示。
    """
    (std_inf, G8_time, gsv) = res
    # 解包数据
    (loc_status, loc_mode, date_UTC, time_UTC, longitude, latitude, longitude_hemisphere, latitude_hemisphere, velocity,
     altitude, direction) = std_inf
    (year, month, day, hour, minute, second) = G8_time

    # 判断定位状态
    if loc_status == 'A':
        str_A = '当前状态：定位有效（A）'
    elif loc_status == 'V':
        str_A = '当前状态：定位无效（V）'

    # 判断定位模式
    if loc_mode == 'A':
        str_B = str_A + ' 自主定位（A）'
    elif loc_mode == 'D':
        str_B = str_A + ' 差分（D）'
    elif loc_mode == 'E':
        str_B = str_A + ' 估算（E）'
    elif loc_mode == 'N':
        str_B = str_A + ' 数据无效（N）'

    # 如果数据有效，拼接显示字符串
    if loc_status != 'V' and loc_mode != 'N':
        # 格式化时间字符串
        str_C = '当前时间：' + str(year).zfill(4) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2) + ' ' + str(
            hour).zfill(2) + ':' + str(minute).zfill(2) + ':' + str(second).zfill(2)
        # 格式化位置
        str_D = '当前位置：' + latitude_hemisphere + '{:.6f}'.format(
            latitude) + '度 ' + longitude_hemisphere + '{:.6f}'.format(longitude) + '度'
        # 格式化速度
        str_E = '当前速度：' + '{:.3f}'.format(velocity) + ' km/h'
        str_F = '当前海拔高度：' + str(altitude)
        str_G = '当前方向：' + str(direction) + '° （0°为北，顺时针方向）'
        # 拼接所有信息
        str_ALL = str_B + '\n' + str_C + '\n' + str_D + '\n' + str_E + '\n' + str_F + '\n' + str_G

        # 生成用于不同Label单独显示的字符串
        str_C1 = str(year).zfill(4) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2) + ' ' + str(
            hour).zfill(2) + ':' + str(minute).zfill(2) + ':' + str(second).zfill(2)
        str_D1 = latitude_hemisphere + '{:.6f}'.format(
            latitude) + '度 ' + longitude_hemisphere + '{:.6f}'.format(longitude) + '度'
        str_E1 = '{:.3f}'.format(velocity) + ' km/h'
        str_F1 = str(altitude)
        str_G1 = str(direction) + '° （0°为北，顺时针方向）'
        str_H1 = str(gsv)
        return str_ALL, str_C1, str_D1, str_E1, str_F1, str_G1, str_H1
    else:
        # 定位无效时的返回值
        str_ALL = '未定位！'
        str_C = '未定位！'
        str_D = '未定位！'
        str_E = '未定位！'
        str_F = '未定位！'
        str_G = '未定位！'
        str_H = '未定位！'
        return str_ALL, str_C, str_D, str_E, str_F, str_G, str_H


# ==========================================
# 主界面类定义
# ==========================================
class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        """
        初始化函数：设置主窗口的定时器、视频写入对象等。
        """
        super(Ui_MainWindow, self).__init__()  # 调用父类初始化
        self.timer_camera = QtCore.QTimer()  # 初始化定时器（本例中未完全启用）

        # 设置视频编解码器为 XVID (用于录制视频)
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')

        # 创建VideoWriter对象，用于保存视频
        # 参数：文件名, 编码器, 帧率, 分辨率
        self.out = cv2.VideoWriter('output.avi', self.fourcc, 20.0, (1920, 1080))
        self.out.release()  # 初始状态先释放，避免占用文件
        self.recording = 0  # 录制标志位，0为停止，1为正在录制
        self.setupUi(self)  # 初始化界面布局

    def setupUi(self, Dialog):
        """
        UI布局函数：手动定义窗口中的按钮、文本框、图形视图等控件及其位置。
        通常这部分代码可由 Qt Designer 生成。
        """
        Dialog.setObjectName("Dialog")
        Dialog.resize(1117, 850)  # 设置窗口大小

        # 定义用于显示视频画面的视图区域
        self.graphicsView = QtWidgets.QGraphicsView(Dialog)
        self.graphicsView.setGeometry(QtCore.QRect(50, 100, 591, 531))  # 设置位置和大小
        self.graphicsView.setObjectName("graphicsView")

        # 按钮1：通常用于开始录像（代码中图标为screenrecording.png）
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(70, 680, 121, 121))
        self.pushButton.setObjectName("pushButton")
        img_path = 'C:\\Users\lenovo\PycharmProjects\pythonProject4\screenrecording.png'  # 图标路径（硬编码）
        self.pushButton.setIcon(QtGui.QIcon(img_path))
        self.pushButton.setIconSize(QtCore.QSize(100, 100))

        # 按钮2：截图按钮
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(239, 680, 121, 121))
        self.pushButton_2.setObjectName("pushButton_2")
        img_path = 'C:\\Users\lenovo\PycharmProjects\pythonProject4\screenshot.png'  # 图标路径
        self.pushButton_2.setIcon(QtGui.QIcon(img_path))
        self.pushButton_2.setIconSize(QtCore.QSize(100, 100))

        # 按钮3：显示视频/开始检测
        self.pushButton_3 = QtWidgets.QPushButton('显示视频', Dialog)
        self.pushButton_3.setGeometry(QtCore.QRect(70, 830, 121, 74))
        self.pushButton_3.setObjectName("pushButton_3")

        # 按钮4：显示文本/开始读取GPS
        self.pushButton_4 = QtWidgets.QPushButton('显示文本', Dialog)
        self.pushButton_4.setGeometry(QtCore.QRect(239, 830, 121, 74))
        self.pushButton_4.setObjectName("pushButton_4")

        # 文本框：用于显示详细的GPS原始信息或汇总信息
        self.textBrowser = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser.setGeometry(QtCore.QRect(440, 680, 681, 224))
        self.textBrowser.setObjectName("textBrowser")

        # 文本框3：显示车辆数量
        self.textBrowser_3 = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser_3.setGeometry(QtCore.QRect(870, 200, 271, 51))
        self.textBrowser_3.setObjectName("textBrowser_3")

        # 标签3：对应文本框3的标题
        self.label3 = QtWidgets.QLabel(Dialog)
        self.label3.setGeometry(QtCore.QRect(720, 200, 201, 51))
        self.label3.setObjectName("label3")
        self.label3.setFont(QFont("Roman times", 15, QFont.Bold))  # 设置字体

        # 文本框4：显示行人数量
        self.textBrowser_4 = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser_4.setGeometry(QtCore.QRect(870, 110, 271, 51))
        self.textBrowser_4.setObjectName("textBrowser_4")

        # 标签4：对应文本框4的标题
        self.label4 = QtWidgets.QLabel(Dialog)
        self.label4.setGeometry(QtCore.QRect(720, 110, 201, 51))
        self.label4.setObjectName("label4")
        self.label4.setFont(QFont("Roman times", 15, QFont.Bold))

        # 以下均为类似的文本框和标签定义（速度、时间、卫星数等）
        self.textBrowser_5 = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser_5.setGeometry(QtCore.QRect(870, 290, 271, 51))
        self.textBrowser_5.setObjectName("textBrowser_5")
        self.label5 = QtWidgets.QLabel(Dialog)
        self.label5.setGeometry(QtCore.QRect(720, 290, 201, 51))
        self.label5.setObjectName("label5")
        self.label5.setFont(QFont("Roman times", 15, QFont.Bold))

        self.textBrowser_6 = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser_6.setGeometry(QtCore.QRect(870, 380, 271, 51))
        self.textBrowser_6.setObjectName("textBrowser_6")
        self.label6 = QtWidgets.QLabel(Dialog)
        self.label6.setGeometry(QtCore.QRect(720, 380, 201, 51))
        self.label6.setObjectName("label6")
        self.label6.setFont(QFont("Roman times", 15, QFont.Bold))

        self.textBrowser_7 = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser_7.setGeometry(QtCore.QRect(870, 470, 271, 51))
        self.textBrowser_7.setObjectName("textBrowser_7")
        self.label7 = QtWidgets.QLabel(Dialog)
        self.label7.setGeometry(QtCore.QRect(720, 470, 201, 51))
        self.label7.setObjectName("label7")
        self.label7.setFont(QFont("Roman times", 15, QFont.Bold))

        self.textBrowser_8 = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser_8.setGeometry(QtCore.QRect(870, 560, 271, 51))
        self.textBrowser_8.setObjectName("textBrowser_8")
        self.label8 = QtWidgets.QLabel(Dialog)
        self.label8.setGeometry(QtCore.QRect(720, 560, 201, 51))
        self.label8.setObjectName("label5")  # 注意：这里ObjectName写错了，应该是label8，但不影响显示
        self.label8.setFont(QFont("Roman times", 15, QFont.Bold))

        # 绑定信号与槽（事件处理）
        self.pushButton_4.clicked.connect(self.text_show)  # 点击"显示文本"触发串口读取
        self.pushButton_3.clicked.connect(self.Screenrecording)  # 点击"显示视频"触发YOLO检测
        self.pushButton_2.clicked.connect(self.Screenshot)  # 点击截图按钮触发截图
        self.pushButton.clicked.connect(self.button_video_click)  # 点击录像按钮触发录像逻辑

        self.retranslateUi(Dialog)  # 设置界面文本
        QtCore.QMetaObject.connectSlotsByName(Dialog)  # 自动关联槽函数

    def retranslateUi(self, Dialog):
        """
        翻译UI函数：设置窗口标题和各个标签的文本内容。
        """
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        # 设置标签的具体文字
        self.label3.setText(_translate("Dialog", "识别到车："))
        self.label4.setText(_translate("Dialog", "识别到人："))
        self.label5.setText(_translate("Dialog", "当前车速："))
        self.label6.setText(_translate("Dialog", "当前时间："))
        self.label7.setText(_translate("Dialog", "卫星数量："))
        self.label8.setText(_translate("Dialog", "地面航向："))

    def Screenshot(self):
        """
        截图功能：获取整个屏幕图像并保存为文件。
        """
        screen = QApplication.primaryScreen()  # 获取主屏幕对象
        pix = screen.grabWindow(QApplication.desktop().winId())  # 抓取整个桌面窗口
        filename, _ = QFileDialog.getSaveFileName(None, 'Save Image', '.', 'Image files (*.jpg *.png)')  # 弹出文件保存对话框
        if filename:  # 如果用户选择了路径
            pix.save(filename)  # 保存图片

    def button_video_click(self):
        """
        录像按钮点击事件：切换录制状态。
        """
        if self.recording == 0:
            self.record_start()  # 开始录制
        elif self.recording == 1:
            self.record_stop()  # 停止录制
        pass

    def record_start(self):
        """
        开始录制视频：初始化VideoWriter。
        """
        # 重新初始化VideoWriter以创建新文件
        self.out = cv2.VideoWriter('output.avi', self.fourcc, 20.0, (1920, 1080))
        self.recording = 1  # 设置标志位

    def record_stop(self):
        """
        停止录制视频。
        """
        self.recording = 0  # 复位标志位

    # ==========================================
    # 核心功能：YOLOv5 检测逻辑
    # ==========================================
    def Screenrecording(self):
        """
        注意：这是一个非常庞大的函数，包含了YOLOv5的推理流程。
        它在主线程中运行，会直接进行模型加载和循环推理。
        """

        # 使用装饰器，优化推理模式（不计算梯度，节省内存）
        @smart_inference_mode()
        def run(
                weights=ROOT / "best_2.pt",  # 权重文件路径
                source=ROOT / "0",  # 数据源（0代表摄像头，也可以是文件路径）
                data=ROOT / "mytrain.yaml",  # 数据集配置文件
                imgsz=(640, 640),  # 推理图片大小
                conf_thres=0.25,  # 置信度阈值
                iou_thres=0.45,  # NMS IOU阈值
                max_det=1000,  # 每张图最大检测数
                device="",  # 设备选择（cuda或cpu）
                view_img=False,  # 是否显示结果
                save_txt=False,  # 是否保存结果到txt
                save_format=0,  # 保存格式
                save_csv=False,  # 是否保存为CSV
                save_conf=False,  # 保存置信度
                save_crop=False,  # 保存截取的目标框图片
                nosave=False,  # 不保存图片/视频
                classes=None,  # 类别过滤
                agnostic_nms=False,  # 跨类别NMS
                augment=False,  # 增强推理
                visualize=False,  # 可视化特征图
                update=False,  # 更新模型
                project=ROOT / "runs/detect",  # 结果保存路径
                name="exp",  # 实验名称
                exist_ok=False,  # 是否允许覆盖
                line_thickness=3,  # 画框线条宽度
                hide_labels=False,  # 隐藏标签
                hide_conf=False,  # 隐藏置信度
                half=False,  # 使用FP16半精度推理
                dnn=False,  # 使用OpenCV DNN加速
                vid_stride=1,  # 视频帧率步长
        ):
            # 处理源路径
            source = str(source)
            save_img = not nosave and not source.endswith(".txt")  # 是否保存推理后的图片
            # 检查文件类型
            is_file = Path(source).suffix[1:] in (IMG_FORMATS + VID_FORMATS)
            is_url = source.lower().startswith(("rtsp://", "rtmp://", "http://", "https://"))
            # 判断是否为摄像头或流媒体
            webcam = source.isnumeric() or source.endswith(".streams") or (is_url and not is_file)
            screenshot = source.lower().startswith("screen")  # 判断是否为屏幕截图流

            if is_url and is_file:
                source = check_file(source)  # 如果是URL文件，先下载

            # 目录设置
            save_dir = increment_path(Path(project) / name, exist_ok=exist_ok)  # 递增实验目录
            (save_dir / "labels" if save_txt else save_dir).mkdir(parents=True, exist_ok=True)  # 创建目录

            # 加载模型
            device = select_device(device)  # 选择设备
            model = DetectMultiBackend(weights, device=device, dnn=dnn, data=data, fp16=half)  # 加载模型
            stride, names, pt = model.stride, model.names, model.pt  # 获取步长、类别名、PyTorch标志
            imgsz = check_img_size(imgsz, s=stride)  # 检查图像尺寸是否符合步长倍数

            # 数据加载器 Dataloader
            bs = 1  # batch_size
            if webcam:
                view_img = check_imshow(warn=True)  # 检查是否支持显示
                # 加载流媒体数据
                dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt, vid_stride=vid_stride)
                bs = len(dataset)
            elif screenshot:
                # 加载屏幕截图数据
                dataset = LoadScreenshots(source, img_size=imgsz, stride=stride, auto=pt)
            else:
                # 加载本地图片/视频数据
                dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt, vid_stride=vid_stride)
            vid_path, vid_writer = [None] * bs, [None] * bs  # 初始化视频写入器列表

            # 运行推理
            model.warmup(imgsz=(1 if pt or model.triton else bs, 3, *imgsz))  # 预热模型（显卡首次运行慢）
            seen, windows, dt = 0, [], (Profile(device=device), Profile(device=device), Profile(device=device))

            # 开始循环处理每一帧
            for path, im, im0s, vid_cap, s in dataset:
                with dt[0]:
                    # 预处理
                    im = torch.from_numpy(im).to(model.device)  # 转为Tensor并放到设备上
                    im = im.half() if model.fp16 else im.float()  # 转换精度
                    im /= 255  # 归一化：0 - 255 转为 0.0 - 1.0
                    if len(im.shape) == 3:
                        im = im[None]  # 增加Batch维度 [H,W,C] -> [1,H,W,C]
                    if model.xml and im.shape[0] > 1:
                        ims = torch.chunk(im, im.shape[0], 0)

                # 推理
                with dt[1]:
                    visualize = increment_path(save_dir / Path(path).stem, mkdir=True) if visualize else False
                    # 模型前向传播
                    if model.xml and im.shape[0] > 1:
                        pred = None
                        for image in ims:
                            if pred is None:
                                pred = model(image, augment=augment, visualize=visualize).unsqueeze(0)
                            else:
                                pred = torch.cat(
                                    (pred, model(image, augment=augment, visualize=visualize).unsqueeze(0)), dim=0)
                        pred = [pred, None]
                    else:
                        pred = model(im, augment=augment, visualize=visualize)

                # NMS (非极大值抑制)
                with dt[2]:
                    # 过滤掉置信度低和重叠度高的框
                    pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)

                # 定义CSV文件路径
                csv_path = save_dir / "predictions.csv"

                # CSV写入函数
                def write_to_csv(image_name, prediction, confidence):
                    """写入预测数据到CSV"""
                    data = {"Image Name": image_name, "Prediction": prediction, "Confidence": confidence}
                    with open(csv_path, mode="a", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=data.keys())
                        if not csv_path.is_file():
                            writer.writeheader()
                        writer.writerow(data)

                # 处理每一张图片的预测结果
                for i, det in enumerate(pred):  # per image
                    seen += 1
                    if webcam:  # batch_size >= 1
                        p, im0, frame = path[i], im0s[i].copy(), dataset.count
                        s += f"{i}: "
                    else:
                        p, im0, frame = path, im0s.copy(), getattr(dataset, "frame", 0)

                    p = Path(p)  # 路径对象
                    save_path = str(save_dir / p.name)  # 图片保存路径
                    txt_path = str(save_dir / "labels" / p.stem) + (
                        "" if dataset.mode == "image" else f"_{frame}")  # 标签保存路径
                    s += "{:g}x{:g} ".format(*im.shape[2:])  # 打印图片尺寸信息
                    gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # 归一化增益 whwh
                    imc = im0.copy() if save_crop else im0  # 备份原图
                    annotator = Annotator(im0, line_width=line_thickness, example=str(names))  # 创建画图工具
                    det_counts = {}  # 创建一个空字典来存储每个类别的检测数量

                    if len(det):
                        # 将预测框从推理尺寸(img_size)映射回原图尺寸(im0 size)
                        det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()

                        # 统计每个类别的数量
                        for c in det[:, 5].unique():
                            n = (det[:, 5] == c).sum()  # 当前类别的数量
                            det_counts[names[int(c)]] = n  # 存储到字典
                            s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # 添加到日志字符串

                        # --- 自定义逻辑：更新UI上的计数 ---
                        personcount = 0
                        carcount = 0
                        # 从字典获取数量
                        if 'person' in det_counts:
                            personcount = det_counts['person']
                        if 'car' in det_counts:
                            carcount = det_counts['car']

                        print(f"人的数量:{personcount},车的数量:{carcount}")
                        # 清空并更新文本框
                        self.textBrowser_4.clear()
                        self.textBrowser_3.clear()
                        self.textBrowser_4.setStyleSheet("font-size: 25pt;")
                        self.textBrowser_4.append(f"<center>{personcount}</center>")  # 显示人数
                        self.textBrowser_3.setStyleSheet("font-size: 25pt;")
                        self.textBrowser_3.append(f"<center>{carcount}</center>")  # 显示车数

                        # 绘制检测框和保存结果
                        for *xyxy, conf, cls in reversed(det):
                            c = int(cls)  # 类别索引
                            label = names[c] if hide_conf else f"{names[c]}"
                            confidence = float(conf)
                            confidence_str = f"{confidence:.2f}"

                            if save_csv:
                                write_to_csv(p.name, label, confidence_str)

                            if save_txt:  # 保存到txt
                                if save_format == 0:
                                    coords = (
                                        (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()
                                    )  # normalized xywh
                                else:
                                    coords = (torch.tensor(xyxy).view(1, 4) / gn).view(-1).tolist()  # xyxy
                                line = (cls, *coords, conf) if save_conf else (cls, *coords)
                                with open(f"{txt_path}.txt", "a") as f:
                                    f.write(("%g " * len(line)).rstrip() % line + "\n")

                            if save_img or save_crop or view_img:  # 画框
                                c = int(cls)
                                label = None if hide_labels else (names[c] if hide_conf else f"{names[c]} {conf:.2f}")
                                annotator.box_label(xyxy, label, color=colors(c, True))
                            if save_crop:
                                save_one_box(xyxy, imc, file=save_dir / "crops" / names[c] / f"{p.stem}.jpg", BGR=True)

                    # 获取绘制了检测框的图像
                    im0 = annotator.result()

                    # --- 核心UI显示逻辑 ---
                    if view_img:
                        """
                        将OpenCV图像转换并显示到PyQt的GraphicsView中
                        """
                        # 注：这里的camera_url似乎只是残留变量，实际使用source参数控制
                        camera_url = "rtsp://192.168.16.17:554/user=admin&password=&channel=1&stream=0.sdp?real_stream"

                        self.scene = QGraphicsScene()  # 创建场景
                        # self.pushButton.setEnabled(False) # 可选：禁用按钮防止重复点击
                        self.graphicsView.setScene(self.scene)  # 将场景设置给视图
                        self.graphicsView.show()  # 显示视图

                        frame = im0  # 获取当前处理后的帧
                        img = frame
                        img = cv2.resize(img, (715, 400), interpolation=cv2.INTER_LINEAR)  # 调整图片尺寸以适配UI
                        cvimg_2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 颜色空间转换：BGR (OpenCV) -> RGB (Qt)
                        y, x = img.shape[:-1]
                        # 创建QImage对象
                        frame = QImage(cvimg_2, x, y, x * 3, QImage.Format_RGB888)

                        self.pix = QPixmap.fromImage(frame)  # 转换为QPixmap
                        self.graphicsView.fitInView(QGraphicsPixmapItem(QPixmap(self.pix)))  # 适应视图大小
                        self.scene.clear()  # 清空旧场景
                        self.scene.addPixmap(self.pix)  # 添加新图片到场景

                        # 视频录制逻辑
                        if self.recording == 1:
                            # 注意：这里使用了pyautogui全屏截图来录制，而不是保存检测后的帧im0
                            # 这会导致性能下降且录制内容包含整个桌面，而非仅仅是摄像头画面
                            img = pyautogui.screenshot()
                            img_rgb = img.convert('RGB')
                            frame = cv2.cvtColor(np.array(img_rgb), cv2.COLOR_RGB2BGR)
                            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                            self.out.write(frame)  # 写入视频文件
                        else:
                            if self.out.isOpened() == 1:
                                self.out.release()  # 停止并释放
                        cv2.waitKey(1)  # OpenCV必须的等待，保持窗口刷新（但在Qt应用中通常不建议混用）

                    # 保存结果视频
                    if save_img:
                        if dataset.mode == "image":
                            cv2.imwrite(save_path, im0)
                        else:  # 'video' or 'stream'
                            if vid_path[i] != save_path:  # new video
                                vid_path[i] = save_path
                                if isinstance(vid_writer[i], cv2.VideoWriter):
                                    vid_writer[i].release()  # release previous video writer
                                if vid_cap:  # video
                                    fps = vid_cap.get(cv2.CAP_PROP_FPS)
                                    w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                                    h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                                else:  # stream
                                    fps, w, h = 30, im0.shape[1], im0.shape[0]
                                save_path = str(
                                    Path(save_path).with_suffix(".mp4"))  # 强制后缀
                                vid_writer[i] = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
                            vid_writer[i].write(im0)

                LOGGER.info(f"{s}{'' if len(det) else '(no detections), '}{dt[1].dt * 1E3:.1f}ms")  # 日志输出推理时间

            # 打印最终统计信息
            t = tuple(x.t / seen * 1e3 for x in dt)
            LOGGER.info(
                f"Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS per image at shape {(1, 3, *imgsz)}" % t)
            if save_txt or save_img:
                s = f"\n{len(list(save_dir.glob('labels/*.txt')))} labels saved to {save_dir / 'labels'}" if save_txt else ""
                LOGGER.info(f"Results saved to {colorstr('bold', save_dir)}{s}")
            if update:
                strip_optimizer(weights[0])  # 更新模型

        # 参数解析函数
        def parse_opt():
            """定义并解析命令行参数"""
            parser = argparse.ArgumentParser()
            parser.add_argument("--weights", nargs="+", type=str, default=ROOT / "best_2.pt",
                                help="model path or triton URL")
            parser.add_argument("--source", type=str, default='0', help="file/dir/URL/glob/screen/0(webcam)")
            parser.add_argument("--data", type=str, default=ROOT / "data/coco128.yaml",
                                help="(optional) dataset.yaml path")
            # ... (其他标准YOLO参数，如conf-thres, iou-thres等，控制检测灵敏度)
            parser.add_argument("--imgsz", "--img", "--img-size", nargs="+", type=int, default=[640],
                                help="inference size h,w")
            parser.add_argument("--conf-thres", type=float, default=0.25, help="confidence threshold")
            parser.add_argument("--iou-thres", type=float, default=0.45, help="NMS IoU threshold")
            parser.add_argument("--max-det", type=int, default=1000, help="maximum detections per image")
            parser.add_argument("--device", default="", help="cuda device, i.e. 0 or 0,1,2,3 or cpu")
            parser.add_argument("--view-img", action="store_true", help="show results")
            parser.add_argument("--save-txt", action="store_true", help="save results to *.txt")
            parser.add_argument(
                "--save-format",
                type=int,
                default=0,
                help="whether to save boxes coordinates in YOLO format or Pascal-VOC format when save-txt is True, 0 for YOLO and 1 for Pascal-VOC",
            )
            parser.add_argument("--save-csv", action="store_true", help="save results in CSV format")
            parser.add_argument("--save-conf", action="store_true", help="save confidences in --save-txt labels")
            parser.add_argument("--save-crop", action="store_true", help="save cropped prediction boxes")
            parser.add_argument("--nosave", action="store_true", help="do not save images/videos")
            parser.add_argument("--classes", nargs="+", type=int,
                                help="filter by class: --classes 0, or --classes 0 2 3")
            parser.add_argument("--agnostic-nms", action="store_true", help="class-agnostic NMS")
            parser.add_argument("--augment", action="store_true", help="augmented inference")
            parser.add_argument("--visualize", action="store_true", help="visualize features")
            parser.add_argument("--update", action="store_true", help="update all models")
            parser.add_argument("--project", default=ROOT / "runs/detect", help="save results to project/name")
            parser.add_argument("--name", default="exp", help="save results to project/name")
            parser.add_argument("--exist-ok", action="store_true", help="existing project/name ok, do not increment")
            parser.add_argument("--line-thickness", default=3, type=int, help="bounding box thickness (pixels)")
            parser.add_argument("--hide-labels", default=False, action="store_true", help="hide labels")
            parser.add_argument("--hide-conf", default=False, action="store_true", help="hide confidences")
            parser.add_argument("--half", action="store_true", help="use FP16 half-precision inference")
            parser.add_argument("--dnn", action="store_true", help="use OpenCV DNN for ONNX inference")
            parser.add_argument("--vid-stride", type=int, default=1, help="video frame-rate stride")
            opt = parser.parse_args()
            opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1  # 扩充imgsz
            print_args(vars(opt))
            return opt

        def main(opt):
            """执行函数"""
            check_requirements(ROOT / "requirements.txt", exclude=("tensorboard", "thop"))
            run(**vars(opt))  # 解包参数并运行run函数

        # 在Screenrecording方法内部直接执行main，这是一个非常规做法
        # 意味着每次点击按钮，都会重新解析参数并启动一个死循环检测
        if __name__ == "__main__":
            opt = parse_opt()
            main(opt)

    # ==========================================
    # 串口数据读取逻辑
    # ==========================================
    def text_show(self):  # 显示文本
        """
        功能：通过串口读取GPS数据并显示。
        严重注意：这里使用 while True 循环且没有放入独立线程，
        一旦运行，Qt主界面将会卡死（无响应），因为主线程被循环占用了。
        """
        flag = 0  # 状态标志，用于记录是否收集齐了GGA和RMC两种数据

        # 初始化串口
        # port: 串口号(COM16), baudrate: 波特率(115200)
        ser = serial.Serial(port="COM16",
                            baudrate=115200,
                            bytesize=serial.EIGHTBITS,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_TWO,
                            timeout=0.5)
        if ser.isOpen():
            print("打开串口" + str(ser.name) + "成功。")
        else:
            print("打开串口失败。")

        while True:  # 死循环读取
            inf = ser.readline()  # 读取一行数据
            if inf.endswith(b'\r\n'):  # 检查行尾
                line = str(inf, "ascii")  # 字节转字符串
                cv2.waitKey(1)  # 这里的waitKey在纯串口逻辑中没有意义，除非为了延时

                # 匹配GPGGA语句（包含海拔、卫星数等）
                if line.startswith('$GPGGA'):
                    loc_GGA = line
                    flag = flag + 1
                # 匹配GPRMC语句（包含时间、经纬度、速度等）
                elif line.startswith('$GPRMC') and flag == 1:
                    loc_RMC = line
                    flag = flag + 1

                # 当flag==2时，说明GGA和RMC都获取到了，可以开始解析
                if flag == 2:
                    # 调用之前定义的解析函数
                    complete, time, position, speed, altitude, direction, sat_sum = print_result(
                        position_get(loc_GGA, loc_RMC))
                    print(complete, time, position, speed, altitude, direction)

                    # 更新UI上的各个文本框
                    self.textBrowser.append('------------GPS Positioning Information------------')
                    self.textBrowser.setStyleSheet("font-size: 23-pt;")
                    self.textBrowser.append(f"<center>{complete}</center>")
                    self.textBrowser.append('------------------------End------------------------\n')

                    self.textBrowser_5.setStyleSheet("font-size: 25pt;")
                    self.textBrowser_5.append(f"<center>{speed}</center>")  # 更新速度

                    self.textBrowser_6.setStyleSheet("font-size: 25pt;")
                    self.textBrowser_6.append(f"<center>{time}</center>")  # 更新时间

                    self.textBrowser_7.setStyleSheet("font-size: 25pt;")
                    self.textBrowser_7.append(f"<center>{sat_sum}</center>")  # 更新卫星数

                    self.textBrowser_8.setStyleSheet("font-size: 25pt;")
                    self.textBrowser_8.append(f"<center>{direction}</center>")  # 更新航向

                    flag = 0  # 重置标志位，准备下一次读取
            else:
                continue


# ==========================================
# 程序入口
# ==========================================
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)  # 创建Qt应用程序实例
    MainWindow = Ui_MainWindow()  # 实例化主窗口类（这里变量名不太规范，通常应当是 MainWindow = QtWidgets.QMainWindow() 然后 ui.setupUi... 但因为类继承了QMainWindow，所以这样写也可以）
    ui = Ui_MainWindow()  # 这里实例化了第二次，实际上是多余的，甚至可能覆盖逻辑
    ui.setupUi(MainWindow)  # 设置UI
    MainWindow.showMaximized()  # 窗口显示时默认最大化
    MainWindow.show()  # 显示窗口

    exit(app.exec_())  # 进入Qt事件循环，直到程序退出