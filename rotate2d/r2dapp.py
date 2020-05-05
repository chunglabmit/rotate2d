from PyQt5 import QtWidgets, QtCore
import sys

from .r2dwindow import R2DWindow

def run_application():
    app = QtWidgets.QApplication(sys.argv)
    window = R2DWindow()
    window.setWindowTitle("Alignment")
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_application()
