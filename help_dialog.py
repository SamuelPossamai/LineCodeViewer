#!/usr/bin/env python3
'''
This file is contains the class that represents the help dialog window, if this file is executed
the help window will appear
'''

import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication

Ui_Help, _ = uic.loadUiType("help.ui")

class Help(QDialog, Ui_Help):
    '''Class that inherits QDialog to create a dialog window showing the program help window'''

    def __init__(self, parent=None):

        QDialog.__init__(self, parent=parent)
        Ui_Help.__init__(self)
        self.setupUi(self)

def __runfile__():
    '''Function called when the file is executed'''
    app = QApplication(sys.argv)

    main = Help()
    main.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    __runfile__()
