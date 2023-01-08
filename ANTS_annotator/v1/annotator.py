import os

from PyQt5.QtGui import QPixmap, QScreen
from PyQt5.QtWidgets import QMainWindow, QRubberBand, QFileDialog
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt

from window_2 import Ui_MainWindow


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
        self.current_image_index = 0

        self.rubberBandList = []
        self.origin = None
        self.rois = []
        self.currentRubberBand = QRubberBand(QRubberBand.Rectangle, self)
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

        if self.count < self.number_files - 1:
            self.current_image_index += 1
            self.count = self.count + 1

            self.showImage()

    def prevImage(self):
        if self.current_image_index != 0:
            self.rubberBandList = [r.hide() for r in self.rubberBandList]
            self.rubberBandList.clear()
            self.rois.clear()

        if self.current_image_index - 1 >= 0:
            self.current_image_index -= 1
            self.showImage()
            # self.showImage(
            #     remain='{:02d}/{}'.format(self.count + 1, self.number_files),
            #     name="%06d.jpg" % self.count)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Right:
            self.nextImage()
        elif event.key() == QtCore.Qt.Key_Left:
            self.prevImage()

    def listFrames(self):
        pass

    def showImage(self, p=None, remain='', name=''):
        if p is None:
            p = self.get_current_image_path()
        pixmap = QPixmap(p)
        scaledPix = pixmap.scaled(self.ui.label.size(), Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        self.ui.label.setPixmap(scaledPix)

    def updateInfo(self):
        pass

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

    def moveEvent(self, event):
        oldScreen = QtWidgets.QApplication.screenAt(event.oldPos())
        newScreen = QtWidgets.QApplication.screenAt(event.pos())

        if (newScreen is not None) and (oldScreen != newScreen):
            self.arangeSize(newScreen)
            self.screenChanged.emit(oldScreen, newScreen)
        self.showImage()
        return super().moveEvent(event)
