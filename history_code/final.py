import sys
import cv2
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
import GNSS
import serial
import detect


class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.setupUi(self)

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1117, 850)
        self.graphicsView = QtWidgets.QGraphicsView(Dialog)
        self.graphicsView.setGeometry(QtCore.QRect(50, 100, 591, 531))
        self.graphicsView.setObjectName("graphicsView")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(70, 680, 121, 121))
        self.pushButton.setObjectName("pushButton")
        img_path = 'C:\\Users\lenovo\PycharmProjects\pythonProject4\screenrecording.png'  # 图片路径
        self.pushButton.setIcon(QtGui.QIcon(img_path))
        self.pushButton.setIconSize(QtCore.QSize(100, 100))  # 设置icon大小
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(240, 680, 121, 121))
        self.pushButton_2.setObjectName("pushButton_2")
        img_path = 'C:\\Users\lenovo\PycharmProjects\pythonProject4\screenshot.png'  # 图片路径
        self.pushButton_2.setIcon(QtGui.QIcon(img_path))
        self.pushButton_2.setIconSize(QtCore.QSize(100, 100))  # 设置icon大小
        self.textBrowser = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser.setGeometry(QtCore.QRect(440, 680, 611, 121))
        #self.textBrowser.text_show()#数据待检查！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser_3 = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser_3.setGeometry(QtCore.QRect(870, 200, 201, 51))
        personcount,carcount=detect.run()
        #self.textBrowser_3.append(str(carcount))#车数，检查！！！！！！！！！！！！！！！！！
        self.textBrowser_3.setObjectName("textBrowser_3")
        self.label3 = QtWidgets.QLabel(Dialog)
        self.label3.setGeometry(QtCore.QRect(720, 200, 201, 51))
        self.label3.setObjectName("label3")
        self.label3.setFont(QFont("Roman times", 15, QFont.Bold))
        self.textBrowser_4 = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser_4.setGeometry(QtCore.QRect(870, 110, 201, 51))
        self.textBrowser_4.setObjectName("textBrowser_4")
        self.label4 = QtWidgets.QLabel(Dialog)
        self.label4.setGeometry(QtCore.QRect(720, 110, 201, 51))
        self.label4.setObjectName("label4")
        self.label4.setFont(QFont("Roman times", 15, QFont.Bold))
        #self.textBrowser_4.append(str(personcount))#人数，检查！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
        self.textBrowser_5 = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser_5.setGeometry(QtCore.QRect(870, 290, 201, 51))
        self.textBrowser_5.setObjectName("textBrowser_5")
        self.label5 = QtWidgets.QLabel(Dialog)
        self.label5.setGeometry(QtCore.QRect(720, 290, 201, 51))
        self.label5.setObjectName("label5")
        self.label5.setFont(QFont("Roman times", 15, QFont.Bold))
        self.textBrowser_6 = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser_6.setGeometry(QtCore.QRect(870, 380, 201, 51))
        self.textBrowser_6.setObjectName("textBrowser_6")
        self.label6 = QtWidgets.QLabel(Dialog)
        self.label6.setGeometry(QtCore.QRect(720, 380, 201, 51))
        self.label6.setObjectName("label6")
        self.label6.setFont(QFont("Roman times", 15, QFont.Bold))
        self.textBrowser_7 = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser_7.setGeometry(QtCore.QRect(870, 470, 201, 51))
        self.textBrowser_7.setObjectName("textBrowser_7")
        self.label7 = QtWidgets.QLabel(Dialog)
        self.label7.setGeometry(QtCore.QRect(720, 470, 201, 51))
        self.label7.setObjectName("label7")
        self.label7.setFont(QFont("Roman times", 15, QFont.Bold))
        self.textBrowser_8 = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser_8.setGeometry(QtCore.QRect(870, 560, 201, 51))
        self.textBrowser_8.setObjectName("textBrowser_8")
        self.label8 = QtWidgets.QLabel(Dialog)
        self.label8.setGeometry(QtCore.QRect(720, 560, 201, 51))
        self.label8.setObjectName("label5")
        self.label8.setFont(QFont("Roman times", 15, QFont.Bold))
        # self.label = QtWidgets.QLabel(Dialog)
        # self.label.setGeometry(QtCore.QRect(70, 680, 121, 121))
        # self.label.setObjectName("label")
        # self.label = QtWidgets.QLabel(Dialog)
        # self.label.setGeometry(QtCore.QRect(240, 680, 121, 121))
        # self.label.setObjectName("label")

        self.pushButton.clicked.connect(self.Screenrecording)  # 按钮“显示图片”连接到函数Screenrecording()
        self.pushButton_2.clicked.connect(self.Screenshot)  # 按钮“显示文本”连接到函数Screenshot()
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        # self.pushButton.setText(_translate("Dialog", "PushButton"))
        # self.pushButton_2.setText(_translate("Dialog", "PushButton"))
        self.label3.setText(_translate("Dialog", "识别到车："))
        self.label4.setText(_translate("Dialog", "识别到人："))
        self.label5.setText(_translate("Dialog", "当前车速："))
        self.label6.setText(_translate("Dialog", "当前时间："))
        self.label7.setText(_translate("Dialog", "卫星数量："))
        self.label8.setText(_translate("Dialog", "地面航向："))


    def Screenshot(self):
        screen = QApplication.primaryScreen()#获取屏幕界面
        self.video_show()
        pix = screen.grabWindow(QApplication.desktop().winId())#截屏
        filename, _ = QFileDialog.getSaveFileName(None, 'Save Image', '.', 'Image files (*.jpg *.png)')#弹出保存界面
        pix.save(filename)

    def Screenrecording(self):
        # 设置视频编解码器
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        # 创建VideoWriter对象
        out = cv2.VideoWriter('output.avi', fourcc, 20.0, (1920, 1080))
        try:
            while True:
                # 截取屏幕上的图像
                img = pyautogui.screenshot()
                # 将截取到的图像转换为RGB格式（PIL格式）
                img_rgb = img.convert('RGB')
                # 将PIL格式的RGB图像转换为OpenCV格式的BGR图像
                frame = cv2.cvtColor(np.array(img_rgb), cv2.COLOR_RGB2BGR)
                # 将图像写入VideoWriter对象
                out.write(frame)
                # 按下'q'键停止录制
                if cv2.waitKey(1) == ord('q'):
                    break
        finally:
            # 释放VideoWriter对象
            out.release()
            # 关闭所有OpenCV窗口
            cv2.destroyAllWindows()


    def video_show(self):  # 调取摄像头
        camera_url = "rtsp://192.168.16.17:554/user=admin&password=&channel=1&stream=0.sdp?real_stream"  # 0.sdp主码流 1次码流
        cap = cv2.VideoCapture(camera_url)
        self.scene = QGraphicsScene()
        self.pushButton.setEnabled(False)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.show()
        while True:
            ret, frame = cap.read()
            img = frame
            img = cv2.resize(img, (715, 400), interpolation=cv2.INTER_LINEAR)  # 图片尺寸调整
            cvimg_2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 把opencv 默认BGR转为通用的RGB
            y, x = img.shape[:-1]
            frame = QImage(cvimg_2, x, y, x * 3, QImage.Format_RGB888)
            self.pix = QPixmap.fromImage(frame)
            self.graphicsView.fitInView(QGraphicsPixmapItem(QPixmap(self.pix)))
            self.scene.clear()
            self.scene.addPixmap(self.pix)
            cv2.waitKey(1)

    def text_show(self):  # 显示文本
        flag = 0
        ser = serial.Serial(port="COM8",
                            baudrate=115200,
                            bytesize=serial.EIGHTBITS,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_TWO,
                            timeout=0.5)
        if ser.isOpen():
            print("打开串口" + str(ser.name) + "成功。")
        else:
            print("打开串口失败。")
        while True:
            self.pushButton_2.setEnabled(False)
            inf = ser.readline()
            if inf.endswith(b'\r\n'):
                line = str(inf, "ascii")
                cv2.waitKey(1)
                if line.startswith('$GPGGA'):
                    loc_GGA = line
                    flag = flag + 1
                elif line.startswith('$GPRMC') and flag == 1:
                    loc_RMC = line
                    flag = flag + 1
                if flag == 2:
                    #b = GNSS.print_result(GNSS.position_get(loc_GGA, loc_RMC))
                    complete,time,position,speed,altitude,direction=GNSS.print_result()
                    self.textBrowser.append('------------GPS Positioning Information------------')
                    self.textBrowser.append(complete)
                    self.textBrowser.append('------------------------End------------------------\n')
                    self.textBrowser_5.append(speed)
                    self.textBrowser_6.append(time)
                    #self.textBrowser_7.append(num)#卫星数量怎么改？
                    self.textBrowser_8.append(direction)
                    flag = 0
            else:
                continue


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.showMaximized()  # 窗口显示时默认最大化
    MainWindow.show()
    exit(app.exec_())