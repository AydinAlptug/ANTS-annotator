import os

import cv2
from PyQt5.QtGui import QPixmap, QScreen
from PyQt5.QtWidgets import QMainWindow, QRubberBand, QFileDialog
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QPoint, QRect, QSize

from window_2 import Ui_MainWindow

import constants

class Annotator(QMainWindow):
    screenChanged = QtCore.pyqtSignal(QScreen, QScreen)

    def __init__(self):
        super().__init__()

        # self.width = self.width
        # self.height = self.height

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setMinimumSize(self.screen().size())

        self.count = 0
        self.number_files = 0
        self.source_path = ""
        self.target_path = ""
        self.images = []
        self.annotated_images_in_cache = set()
        self.scale_x = 1
        self.scale_y = 1
        self.x_0 = 0
        self.y_0 = 0
        self.current_image_index = 0

        self.rubberBandList = []
        self.origin = None
        self.rois = []
        self.currentRubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.currentClickPointValid = False
        self.currentReleasePointValid = False
        self.imageLabel = self.ui.label
        self.mode = self.ui.checkBox.isChecked()
        self.ui.textEdit_5.setDisabled(True)
        self.ui.horizontalLayout_8.setContentsMargins(-1, -1, -1, self.height() * 0.65)
        self.ui.label.setMinimumSize(self.width(), self.height() * 0.65)
        self.ui.label.setStyleSheet("border: 2px solid black;")

        # Button listeners
        self.ui.selectSourceButton.clicked.connect(self.loadSelectedSourceFolder)

        self.ui.pushButton.clicked.connect(self.processImage)

        self.ui.pushButton_2.clicked.connect(self.clear)

        self.ui.pushButton_3.clicked.connect(self.nextImage)
        self.ui.pushButton_4.clicked.connect(self.prevImage)
        self.ui.pushButton_3.keyPressEvent = self.keyPressEvent
        self.ui.pushButton_4.keyPressEvent = self.keyPressEvent

        self.ui.pushButton_5.clicked.connect(self.listFrames)
        self.label_max_width = self.ui.label.size().width()
        self.label_max_height = self.ui.label.size().height()

        self.showMaximized()

    def processImage(self):
        pass

    def clear(self):
        pass

    def nextImage(self):
        if self.current_image_index != len(self.images):
            self.rubberBandList = [r.hide() for r in self.rubberBandList]
            self.rubberBandList.clear()
            self.rois.clear()

        if self.current_image_index < self.number_files - 1:
            self.current_image_index += 1
            self.showImage()
        self.updateInfo()

    def prevImage(self):
        if self.current_image_index != 0:
            self.rubberBandList = [r.hide() for r in self.rubberBandList]
            self.rubberBandList.clear()
            self.rois.clear()

        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.showImage()
            # self.showImage(
            #     remain='{:02d}/{}'.format(self.count + 1, self.number_files),
            #     name="%06d.jpg" % self.count)
        self.updateInfo()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Right:
            self.nextImage()
        elif event.key() == QtCore.Qt.Key_Left:
            self.prevImage()

    def listFrames(self):
        pass

    def showImage(self, path=None, remain='', name=''):
        if path is None:
            if(self.current_image_index in self.annotated_images_in_cache):
                path = f'runtime_cache\\with_bbox_{self.current_image_index}.png'
            else:
                path = self.get_current_image_path()
        pixmap = QPixmap(path)
        scaledPix = pixmap.scaled(self.ui.label.size(), Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        self.ui.label.setPixmap(scaledPix)
        self.ui.label.setStyleSheet("border: 1px solid black;")
        self.ui.label.setFixedSize(scaledPix.width(), scaledPix.height())

        self.scale_x = self.ui.label.size().width()
        self.scale_y = self.ui.label.size().height()

        self.x_0 = (self.label_max_width - scaledPix.width()) / 2
        self.y_0 = self.ui.label.y()


    def updateInfo(self):
        self.ui.label_2.setText("Frame: "
                                + str(self.current_image_index + 1)
                                + " / "
                                + str(len(self.images)))

    def loadSelectedSourceFolder(self):
        self.count = 0
        folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.set_fields(folderpath)
        list = os.listdir(folderpath)  # dir is your directory path

        self.number_files = len(list)
        self.ui.textEdit_5.setText(folderpath)
        self.showImage()

    def set_fields(self, source):
        self.source_path = source + "/"

        self.images = sorted(os.listdir(self.source_path))
        self.images.sort(key=lambda x: int(x.split('.')[0]))

        self.number_files = len(self.images)

    def get_current_image_path(self):
        p = None
        try:
            p = self.source_path + self.images[self.current_image_index]
        except Exception as e:
            print("An error occured: ", e)
        return p

    def arangeSize(self, newScreen=None):
        if newScreen is not None:
            screenRect = newScreen.size()

        self.setFixedWidth(screenRect.width())
        self.setFixedHeight(screenRect.height())

        self.ui.horizontalLayout_8.setContentsMargins(-1, -1, -1, self.height() * 0.65)
        self.ui.label.setFixedSize(self.width(), self.height() * 0.65)
        self.label_max_width = self.ui.label.size().width()
        self.label_max_height = self.ui.label.size().height()

    def moveEvent(self, event):
        oldScreen = QtWidgets.QApplication.screenAt(event.oldPos())
        newScreen = QtWidgets.QApplication.screenAt(event.pos())

        if (newScreen is not None) and (oldScreen != newScreen):
            self.arangeSize(newScreen)
            self.screenChanged.emit(oldScreen, newScreen)
        self.showImage()
        return super().moveEvent(event)

    def mousePressEvent(self, event):

        q_point = QPoint(event.pos())

        if event.button() == Qt.LeftButton:

            h, w, c = cv2.imread(self.source_path + self.images[self.current_image_index]).shape  # current image shape

            self.origin = q_point

            if self.isInImage(q_point):
                self.currentClickPointValid = True
                newRubberBand = QRubberBand(QRubberBand.Rectangle, self)
                newRubberBand.setGeometry(QRect(self.origin, QSize()))

                if q_point.y() <= h and q_point.x() <= w:  # prevent outside boxes
                    point = q_point
                    if self.isInImage(point):
                        self.rubberBandList.append(newRubberBand)
                        newRubberBand.show()
                        self.currentRubberBand = newRubberBand
            else:
                self.currentClickPointValid = False

        if event.button() == Qt.RightButton:
            point = q_point
            for r in self.rubberBandList:
                if self.isInRect(point, list(r.geometry().getRect())):
                    r.hide()
                    self.rubberBandList.remove(r)
                    if self.rois.__contains__(list(r.geometry().getRect())):
                        self.rois.remove(list(r.geometry().getRect()))
                    self.origin = None

    def isInRect(self, point, rect):
        xp = point.x()
        yp = point.y()

        x1, y1, w, h = rect
        x2, y2 = x1 + w, y1 + h

        if x1 < xp and xp < x2:
            if y1 < yp and yp < y2:
                return True
        return False

    def isInImage(self, point):
        xp = point.x()
        yp = point.y()

        x1 = self.ui.label.geometry().x()
        y1 = self.ui.label.geometry().y()
        w = self.ui.label.geometry().width()
        h = self.ui.label.geometry().height()

        x2, y2 = x1 + w, y1 + h

        if x1 < xp and xp < x2:
            if y1 < yp and yp < y2:
                return True
        return False

    def read_image(self):
        if(self.current_image_index in self.annotated_images_in_cache):
            path = f'runtime_cache\\with_bbox_{self.current_image_index}.png'
        else:
            path = self.source_path + self.images[self.current_image_index]
        img_raw = cv2.imread(path)
        return img_raw

    def transform(self, roi):
        # 0,0 0,h
        # w,0 w,h
        img_raw = self.read_image()
        h, w, c = img_raw.shape
        print("R", roi)
        roi = [0 if x < 0 else x for x in roi]
        if roi[0] > w or roi[1] > h:
            return None
        if roi[0] > w and roi[1] > h:
            roi[0] = w
            roi[1] = h

        if roi[2] == roi[3] == 0:
            x1, x2, y1, y2 = self.scaleSelectionToAnnotate(h, roi, w)
            self.drawBBoxAndCacheImage(img_raw, x1, x2, y1, y2)
            self.showImage()

        return roi

    def scaleSelectionToAnnotate(self, h, roi, w):
        half_x = constants.BBOX_SHAPE[0] / 2
        half_y = constants.BBOX_SHAPE[1] / 2
        scale_ratio_x = w / self.scale_x
        scale_ratio_y = h / self.scale_y
        x1 = int(((roi[0] - self.x_0) * scale_ratio_x) - half_x)  # -  half_x
        x2 = int(((roi[0] - self.x_0 + roi[2]) * scale_ratio_x) + half_x)
        y1 = int(((roi[1] - self.y_0) * scale_ratio_y) - half_y)
        y2 = int(((roi[1] - self.y_0 + roi[3]) * scale_ratio_y) + half_y)
        return x1, x2, y1, y2

    def drawBBoxAndCacheImage(self, img_raw, x1, x2, y1, y2):
        cv2.rectangle(img_raw, (x1, y1), (x2, y2), (0, 0, 255), 1)
        cache_path = f'runtime_cache\\with_bbox_{self.current_image_index}.png'
        cv2.imwrite(cache_path, img_raw)
        self.annotated_images_in_cache.add(self.current_image_index)

    def mouseMoveEvent(self, event):
        if not (self.origin is None or self.origin.isNull()):
            if event.button() == Qt.RightButton:
                return
            point = QPoint(event.pos())
            if self.isInImage(point) and self.currentClickPointValid:
                self.currentRubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            rect = list(self.currentRubberBand.geometry().getRect())

            point = QPoint(event.pos())
            if self.isInImage(point):
                rect = self.transform(rect)
                if rect is not None:
                    self.currentReleasePointValid = True
                    self.rois.append(rect)
            else:
                self.currentReleasePointValid = False
            # self.rubberBand.hide()
