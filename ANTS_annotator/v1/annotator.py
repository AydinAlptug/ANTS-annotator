from PyQt5.QtWidgets import QMainWindow, QRubberBand

from window_2 import Ui_MainWindow

class Annotator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.rubberBandList = []
        self.origin = None
        self.rois = []
        self.currentRubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.imageLabel = self.ui.label
        self.mode = self.ui.checkBox.isChecked()

        # Button listeners
        self.ui.pushButton.clicked.connect(self.process_image)

        self.ui.pushButton_2.clicked.connect(self.clear)

        self.ui.pushButton_3.clicked.connect(self.next_image)
        self.ui.pushButton_4.clicked.connect(self.prev_image)
        self.ui.pushButton_3.keyPressEvent = self.keyPressEvent
        self.ui.pushButton_4.keyPressEvent = self.keyPressEvent

        self.ui.pushButton_5.clicked.connect(self.list_frames)

        self.showImage()
        self.updateInfo()

    def process_image(self):
        pass
    def clear(self):
        pass
    def next_image(self):
        pass
    def prev_image(self):
        pass
    def list_frames(self):
        pass
    def showImage(self):
        pass
    def updateInfo(self):
        pass