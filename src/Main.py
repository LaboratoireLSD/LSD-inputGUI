'''
Created on 2009-06-26

@author:  Majid Malis
@contact: mathieu.gagnon.10@ulaval.ca
@organization: Universite Laval

@license
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 
'''
#import sip
#sip.setapi('QString', 1)
#sip.setapi('QVariant', 1) 

from PyQt4.QtGui import QApplication, QIcon, QPixmap, QSplashScreen
from frame.MainFrame import MainWindow
from PyQt4.QtCore import QString
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
