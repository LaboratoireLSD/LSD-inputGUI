
#import sip
#sip.setapi('QString', 1)
#sip.setapi('QVariant', 1) 

from PyQt4.QtGui import QApplication, QIcon, QPixmap, QSplashScreen
from frame.MainFrame import MainWindow
import sys
import os


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pixmap = QPixmap("Tests/psycho.jpg")
    splashcreen = QSplashScreen(pixmap)
    splashcreen.show()
    app.setOrganizationName("Laboratoire de Simulation et de Depistage")
    app.setApplicationName("LSD Simulator Dashboard")
    app.setWindowIcon(QIcon("../img/icon.png"))
    app.window = MainWindow()
    app.window.setWindowTitle("LSD Simulator Dashboard -- version alpha")
    if sys.argv[0].rpartition("/")[0]:
        os.chdir(sys.argv[0].rpartition("/")[0])
    app.window.loadSettings()
    splashcreen.finish(app.window)
    sys.exit(app.exec_())
