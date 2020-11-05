# By Fivethousand
import sys

from PyQt5 import QtWidgets, Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication
from config import background_img
from mainwindow import Ui_Form
import numpy as np
import threading
import  time
from cv2 import *
import cv2
import copy

point_color = (0, 255, 0)  # BGR
thickness = 5
lineType = 4
class Scanning_camera(QtWidgets.QMainWindow,Ui_Form):
    def __init__(self,parent=None):
        super(Scanning_camera, self).__init__(parent)
        self.setupUi(self)
        self.init_UI()
        self.init_data()
        self.init_connect()
        self.online()

    def init_UI(self):
        self.label_screen.setPixmap(QPixmap(background_img))
        self.label_screen.setScaledContents(True)

    def init_data(self):
        self.working=True
        self.playing=True
        self.videoCap=VideoCapture(0)
        self.line_index=0
        self.count_down=0
        self.speed_adapter=1    # control the speed of the movement of the line, the value of line_index would alter in every (speed_adapter) count.
        self.mode='vertical'    # value in ['horizontal','vertical'], which defines that the line scans horizontally or vertically
        self.video_width= int(self.videoCap.get(CAP_PROP_FRAME_WIDTH)) # float
        self.video_height = int(self.videoCap.get(CAP_PROP_FRAME_HEIGHT) )# float
        self.fixed_part=np.zeros((self.video_height,self.video_width,3),np.uint8)

    def init_connect(self):
        self.btn_restart.clicked.connect(self.restart)
    def restart(self):
        self.playing=False
        self.line_index=0
        self.count_down=0
        time.sleep(0.2)
        self.playing=True
    def online(self):
        self.video_thread = threading.Thread(target=self.play)
        self.video_thread.start()

    def pause(self):
        self.playing=False

    def close(self):
        self.playing=False
        self.working=False
    def play(self):
        '''
        this function would be triggered by the function 'online' and run as a thread.
        :param src:   the path of video to be played
        :return:
        '''

        while self.working:
            while self.playing:
                flag,frame=self.videoCap.read()
                if flag:
                    frame=flip(frame,1,180)
                    assert self.mode in ['horizontal','vertical']

                    if self.mode is 'horizontal':
                        ptStart = (0, 0 + self.line_index)
                        ptEnd = (self.video_width, 0 + self.line_index)
                        if self.count_down == 0:
                            self.line_index += 1
                            if self.line_index >= self.video_height:
                                self.pause()


                            self.fixed_part[self.line_index:, :, :] = frame[self.line_index:, :, :]


                    else:
                        ptStart =(0+self.line_index,0)
                        ptEnd=(0+self.line_index,self.video_height)
                        if self.count_down == 0:
                            self.line_index += 1
                            if self.line_index >= self.video_width:
                                self.pause()

                                self.fixed_part[:, self.line_index:, :] = frame[:, self.line_index:, :]
                            self.fixed_part[:, self.line_index:, :] = frame[:, self.line_index:, :]
                    ss=self.fixed_part.copy()
                    cv2.line(ss, ptStart, ptEnd, point_color, thickness, lineType)
                    show = cv2.cvtColor(ss, cv2.COLOR_BGR2RGB)  # 将BGR转化成RGB
                    # show = cv2.resize(frame, (int(self.label_screen.self.video_width()*0.9), int(self.label_screen.self.video_height()*0.9)),
                    #                    interpolation=cv2.INTER_AREA)
                    showImage = QImage(show, show.shape[1], show.shape[0],
                                       QImage.Format_RGB888)  # 转换成QImage类型
                    self.label_screen.setPixmap(QPixmap.fromImage(showImage))

                    self.count_down = (self.count_down + 1) % self.speed_adapter

                    time.sleep(0.01)
                else:
                    break
            time.sleep(0.05)

    def closeEvent(self, event):
        self.close()

if __name__ == '__main__':
    if __name__ == '__main__':
        app = QApplication(sys.argv)
        myWin = Scanning_camera()
        myWin.show()

        sys.exit(app.exec_())