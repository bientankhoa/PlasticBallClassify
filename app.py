import math
import serial
import numpy as np
import PyQt5
from PyQt5 import uic, QtGui
from PyQt5.QtCore import QTimer
import sys
import queue
import threading
import cv2
from PyQt5.QtWidgets import QPushButton

sys.path.append('...')
form_class = uic.loadUiType("theme.ui")[0]
ser = serial.Serial('com3', 9600)
global each, per, flag, temp_r, temp_b, temp_y, temp_w, temp_g, r_c, b_c, y_c, w_c, g_c, red, green, blue
global red_r, red_g, red_b, blue_r, blue_g, blue_b, white_r, white_g, white_b, yellow_r, yellow_g, yellow_b, green_r, green_g, green_b
each = 3
flag = 0
r_c = 0
b_c = 0
y_c = 0
w_c = 0
g_c = 0
temp_r = 0
temp_b = 0
temp_g = 0
temp_w = 0
temp_y = 0
(red_r, red_g, red_b) = (165, 68, 53)
(blue_r, blue_g, blue_b) = (35, 85, 155)
(yellow_r, yellow_g, yellow_b) = (125, 135, 68)
(green_r, green_g, green_b) = (90, 140, 105)
(white_r, white_g, white_b) = (118, 120, 125)

running = False
capture_thread = None
q = queue.Queue()


def grab(cam, queue, width, height, fps):
    global running
    capture = cv2.VideoCapture(cam)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    capture.set(cv2.CAP_PROP_FPS, fps)
    while (running):
        frame = {}
        capture.grab()
        retval, img = capture.retrieve(0)
        frame["img"] = img
        if queue.qsize() < 1:
            queue.put(frame)


class OwnImageWidget(PyQt5.QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(OwnImageWidget, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        self.image = image
        sz = image.size()
        self.setMinimumSize(sz)
        self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(PyQt5.QtCore.QPoint(0, 0), self.image)
        qp.end()


class MyWindowClass(PyQt5.QtWidgets.QMainWindow, form_class):
    def __init__(self, parent=None):

        PyQt5.QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.label.setStyleSheet(
            "color: white;")
        self.label_2.setStyleSheet(
            "color: white;")
        self.setStyleSheet("background-color:#002233")
        self.red.setStyleSheet(
            "background-color: red; border-radius: 30%; font-size: 30px;")
        self.rednum.setStyleSheet(
            "background-color: white; font-size: 30px;")
        self.blue.setStyleSheet(
            "background-color: blue; border-radius: 30%;")
        self.bluenum.setStyleSheet(
            "background-color: white; font-size: 30px;")
        self.yellow.setStyleSheet(
            "background-color: yellow; border-radius: 30%;")
        self.yellownum.setStyleSheet(
            "background-color: white; font-size: 30px;")
        self.green.setStyleSheet(
            "background-color: green; border-radius: 30%;")
        self.greennum.setStyleSheet(
            "background-color: white; font-size: 30px;")
        self.white.setStyleSheet(
            "background-color: white; border-radius: 30%; font-size: 30px; padding: 10px")
        self.whitenum.setStyleSheet(
            "background-color: white; font-size: 30px;")
        self.redpicker.setStyleSheet(
            "background-color: red; border-radius: 5%; color: black; font-size: 20px;")
        self.bluepicker.setStyleSheet(
            "background-color: blue; border-radius: 5%; color: black; font-size: 20px;")
        self.yellowpicker.setStyleSheet(
            "background-color: yellow; border-radius: 5%; color: black; font-size: 20px;")
        self.greenpicker.setStyleSheet(
            "background-color: green; border-radius: 5%; color: black; font-size: 20px;")
        self.whitepicker.setStyleSheet(
            "background-color: white; border-radius: 5%; color: black; font-size: 20px;")
        self.clear.setStyleSheet(
            "background-color: gray; color: black; border-radius: 10%; font-size: 20px; padding: 10px")
        self.colorpicker.setStyleSheet(
            "background-color: white; color: black; border-radius: 10%; font-size: 20px; padding: 10px;")
        self.accurate.setStyleSheet(
            "background-color: white; color: black; border-radius: 10%; font-size: 20px; padding: 10px;")
        self.clear.clicked.connect(self.reset)
        self.redpicker.clicked.connect(self.red_picker)
        self.yellowpicker.clicked.connect(self.yellow_picker)
        self.whitepicker.clicked.connect(self.white_picker)
        self.greenpicker.clicked.connect(self.green_picker)
        self.bluepicker.clicked.connect(self.blue_picker)
        self.rednum.setText(str(r_c))
        self.bluenum.setText(str(b_c))
        self.yellownum.setText(str(y_c))
        self.greennum.setText(str(g_c))
        self.whitenum.setText(str(w_c))
        self.window_width_03 = self.screen03.frameSize().width()
        self.window_height_03 = self.screen02.frameSize().height()
        self.screen03 = OwnImageWidget(self.screen03)
        self.window_height_02 = self.screen02.frameSize().height()
        self.window_width_02 = self.screen01.frameSize().width()
        self.screen02 = OwnImageWidget(self.screen02)
        self.window_height_01 = self.screen01.frameSize().height()
        self.window_width_01 = self.screen01.frameSize().width()
        self.screen01 = OwnImageWidget(self.screen01)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(200)
        global running
        running = True
        capture_thread.start()

    def reset(self):
        global r_c, b_c, y_c, g_c, w_c
        global flag
        r_c = 0
        self.rednum.setText(str(r_c))
        b_c = 0
        self.bluenum.setText(str(b_c))
        y_c = 0
        self.yellownum.setText(str(y_c))
        g_c = 0
        self.greennum.setText(str(g_c))
        w_c = 0
        self.whitenum.setText(str(w_c))
        flag = 0
        print(flag)

    def red_picker(self):
        (red_r, red_g, red_b) = (red, green, blue)
        print(red_r, red_g, red_b)

    def blue_picker(self):
        (blue_r, blue_g, blue_b) = (red, green, blue)
        print((blue_r, blue_g, blue_b))

    def yellow_picker(self):
        (yellow_r, yellow_g, yellow_b) = (red, green, blue)
        print((yellow_r, yellow_g, yellow_b))

    def green_picker(self):
        (green_r, green_g, green_b) = (red, green, blue)
        print((green_r, green_g, green_b))

    def white_picker(self):
        (white_r, white_g, white_b) = (red, green, blue)
        print((white_r, white_g, white_b))

    def update_frame(self):
        global r_c, y_c, g_c, w_c, b_c, red, green, blue, flag, temp_r, temp_b, temp_y, temp_w, temp_g
        if not q.empty():
            frame = q.get()
            img = frame["img"]
            img_height, img_width, img_colors = img.shape
            scale_w_03 = float(self.window_width_03) / float(img_width)
            scale_h_03 = float(self.window_height_03) / float(img_height)
            scale_03 = min([scale_w_03, scale_h_03])
            scale_w_02 = float(self.window_width_02) / float(img_width)
            scale_h_02 = float(self.window_height_02) / float(img_height)
            scale_02 = min([scale_w_02, scale_h_02])
            scale_w_01 = float(self.window_width_01) / float(img_width)
            scale_h_01 = float(self.window_height_01) / float(img_height)
            scale_01 = min([scale_w_01, scale_h_01])
            if scale_01 == 0:
                scale_01 = 1
            if scale_02 == 0:
                scale_02 = 1
            if scale_03 == 0:
                scale_03 = 1
            img_01 = cv2.resize(img, None, fx=1, fy=1, interpolation=cv2.INTER_CUBIC)
            img_01 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_02 = cv2.resize(img, None, fx=scale_03, fy=scale_03, interpolation=cv2.INTER_CUBIC)
            img_02 = cv2.cvtColor(img_02, cv2.COLOR_BGR2GRAY)
            img_03 = cv2.resize(img, None, fx=scale_03, fy=scale_03, interpolation=cv2.INTER_CUBIC)
            img_03 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_03 = cv2.circle(img_03, (380, 285), 150, (255, 0, 0), 4)
            img_03 = cv2.circle(img_03, (380, 285), 156, (0, 255, 0), 4)
            img_03 = cv2.rectangle(img_03, (490, 375), (270, 195), (0, 0, 255), 4)
            img_02 = cv2.GaussianBlur(img_02, (5, 5), 0)
            img_02 = cv2.medianBlur(img_02, 5)
            img_02 = cv2.adaptiveThreshold(img_02, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 3.5)
            kernel = np.ones((5, 5), np.uint8)
            img_02 = cv2.erode(img_02, kernel, iterations=1)
            img_02 = cv2.dilate(img_02, kernel, iterations=1)

            img_04 = cv2.resize(img, None, fx=1, fy=1, interpolation=cv2.INTER_CUBIC)
            img_04 = cv2.cvtColor(img_04, cv2.COLOR_BGR2GRAY)
            img_04 = cv2.GaussianBlur(img_04, (5, 5), 0)
            img_04 = cv2.medianBlur(img_04, 5)
            img_04 = cv2.adaptiveThreshold(img_04, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2.5)
            kernel = np.ones((1, 1), np.uint8)
            img_04 = cv2.erode(img_04, kernel, iterations=1)
            img_04 = cv2.dilate(img_04, kernel, iterations=1)
            circles = cv2.HoughCircles(img_04, cv2.HOUGH_GRADIENT, 1, 100, param1=40, param2=45, minRadius=20,
                                       maxRadius=300)
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")

                for (x, y, r) in circles:
                    if (x < 490 and x > 270):
                        if (y < 375 and y > 195) and (
                                x + r < 530 and y + r < 435 and x - r > 230 and y - r > 135 and r > 50):
                            cv2.circle(img_04, (x, y), r, (0, 255, 0), -1)
                            roi = img_03[y - r: y + r, x - r: x + r]
                            width, height = roi.shape[:2]
                            mask = np.zeros((width, height, 3), roi.dtype)
                            cv2.circle(mask, (int(width / 2), int(height / 2)), r, (255, 255, 255), -1)
                            dst = cv2.bitwise_and(roi, mask)
                            data = []
                            for i in range(3):
                                channel = dst[:, :, i]
                                indices = np.where(channel != 0)[0]
                                color = np.mean(channel[indices])
                                data.append(int(color))
                            red, green, blue = data
                            self.colorpicker.setText(str(red) + "-" + str(green) + "-" + str(blue))
                            print(data)
                            cv2.circle(img_03, (x, y), r, (red, green, blue), -1)
                            dr = math.sqrt(
                                pow((red - red_r), 2) + pow((green - red_g), 2) + pow((blue - red_b), 2))
                            db = math.sqrt(
                                pow((red - blue_r), 2) + pow((green - blue_g), 2) + pow((blue - blue_b), 2))
                            dy = math.sqrt(
                                pow((red - yellow_r), 2) + pow((green - yellow_g), 2) + pow((blue - yellow_b), 2))
                            dg = math.sqrt(
                                pow((red - green_r), 2) + pow((green - green_g), 2) + pow((blue - green_b), 2))
                            dw = math.sqrt(
                                pow((red - white_r), 2) + pow((green - white_g), 2) + pow((blue - white_b), 2))
                            find_color = [dr, db, dg, dy, dw]
                            result = min(find_color)
                            print(result)

                            if (result == dr and flag != 1):
                                r_c += 1
                                flag = 1
                                per = dr / math.sqrt(red_r * red_r + red_b * red_b + red_g * red_g)
                                self.rednum.setText(str(r_c))
                                self.accurate.setText(str(100 - int(per * 100)) + "%")
                                print(flag)
                                ser.write(str.encode(str(flag)))
                                #time.sleep(each)
                            elif (result == db and flag != 2):
                                b_c += 1
                                flag = 2
                                per = db / math.sqrt(255 * 255 + 255 * 255 + 255 * 255)
                                self.bluenum.setText(str(b_c))
                                self.accurate.setText(str(100 - int(per * 100)) + "%")
                                print(flag)
                                ser.write(str.encode(str(flag)))
                                #time.sleep(each)
                            elif (result == dg and flag != 3):
                                g_c += 1
                                flag = 3
                                per = dg / math.sqrt(255 * 255 + 255 * 255 + 255 * 255)
                                self.greennum.setText(str(g_c))
                                self.accurate.setText(str(100 - int(per * 100)) + "%")
                                ser.write(str.encode(str(flag)))
                                #time.sleep(each)
                                print(flag)
                            elif (result == dw and flag != 4):
                                w_c += 1
                                flag = 4
                                per = dw / math.sqrt(255 * 255 + 255 * 255 + 255 * 255)
                                self.whitenum.setText(str(w_c))
                                self.accurate.setText(str(100 - int(per * 100)) + "%")
                                ser.write(str.encode(str(flag)))
                                #time.sleep(each)
                                print(flag)
                            elif (result == dy and flag != 5):
                                y_c += 1
                                flag = 5
                                per = dy / math.sqrt(255 * 255 + 255 * 255 + 255 * 255)
                                self.yellownum.setText(str(y_c))
                                self.accurate.setText(str(100 - int(per * 100)) + "%")
                                ser.write(str.encode(str(flag)))
                                #time.sleep(each)
                                print(flag)

            height_01, width_01, bpc_01 = img_01.shape
            height_02, width_02 = img_02.shape
            height_03, width_03, bpc_03 = img_03.shape
            height_04, width_04 = img_04.shape
            bpl_01 = 3 * width_01
            bpl_03 = 3 * width_03
            image_01 = QtGui.QImage(img_04.data, width_04, height_04, QtGui.QImage.Format_Grayscale16)
            image_02 = QtGui.QImage(img_02.data, width_02, height_02, QtGui.QImage.Format_Grayscale8)
            image_03 = QtGui.QImage(img_03.data, width_03, height_03, bpl_03, QtGui.QImage.Format_RGB888)
            image_04 = QtGui.QImage(img_04.data, width_04, height_04, QtGui.QImage.Format_Grayscale8)
            self.screen01.setImage(image_01)
            self.screen02.setImage(image_02)
            self.screen03.setImage(image_03)


capture_thread = threading.Thread(target=grab, args=(0, q, 760, 570, 5))
app = PyQt5.QtWidgets.QApplication(sys.argv)
w = MyWindowClass(None)
w.setWindowTitle('Color ball detection application')
w.show()
app.exec_()
