#!/usr/bin/env python3

import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication

Ui_Help, _ = uic.loadUiType("help.ui")

class Help(QDialog, Ui_Help):
    
    def __init__(self, parent=None):
        
        QDialog.__init__(self)
        Ui_Help.__init__(self)
        self.setupUi(self)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = Help()
    main.show()

    sys.exit(app.exec_())
