from PyQt5.QtWidgets import QApplication
from annotator import Annotator

if __name__ == "__main__":
    app = QApplication([])
    wind = Annotator()
    wind.show()
    app.exec()