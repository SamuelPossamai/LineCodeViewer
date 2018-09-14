#!/usr/bin/env python3

import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QKeyEvent

from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from about import About
from help_dialog import Help

import linecodes

Ui_MainWindow, _ = uic.loadUiType("mainwindow.ui")

class MainWindow(QMainWindow, Ui_MainWindow):
    
    def __init__(self, parent=None):
        
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        self.ax = None
        self.ax2 = None
        
        self.timer = QTimer(self)

        self.horizontalSlider.hide()
        self.VizualizationSpinBox.hide()
        
        self.create_graph()
        
        self.create_code_f_dict()
        self.init_connect()
        
        self.stringInputRadioButton.setChecked(True)
        
        self.lineEdit.setFocus()
        
        self.must_update_graph = 0
        
        self.update_combo_box()
        
        self.timer.setInterval(150)
        self.timer.start()
    
    def partial_vizualization_state_changed(self):
        
        self.horizontalSlider.setVisible(self.partialVizualizationCheckBox.isChecked())
        self.VizualizationSpinBox.setVisible(self.partialVizualizationCheckBox.isChecked())
        self.update_axis()
    
    def order_graph_update(self):

        self.must_update_graph = 1

    def update_graph(self):
        
        if self.must_update_graph == 2:
            self.must_update_graph = 0;
            self.plot()
        
        elif self.must_update_graph >= 1:
            self.must_update_graph += 1

    def read_bin_lineedit(self):
        
        self.ax = None
        self.ax2 = None
        
        word = self.lineEdit.text()
        
        if len(word) == 0:
            self.canvas.draw()
            self.hexLabel.setText('-')
            self.binLabel.setText('-')
            return None
        
        if self.binInputRadioButton.isChecked():
            
            binary = word
            
            if(len(binary) > 2):
                if(binary[0] == '0' and ( binary[1] == 'b' or binary[1] == 'B')):
                    binary = binary[2:]
            
            hx = self.bin_to_hex(binary)
            
            if hx is None:
                self.canvas.draw()
                self.hexLabel.setText('-')
                self.binLabel.setText('Binário Invalido')
                return None

        else:
            
            if self.hexInputRadioButton.isChecked():
                hx = word
            else:
                hx = self.word_to_hex(word)
        
            if(len(hx) > 2):
                if(hx[0] == '0' and ( hx[1] == 'x' or hx[1] == 'X')):
                    hx = hx[2:]
            
            binary = self.hex_to_binary(hx)
        
            if binary is None:
                self.canvas.draw()
                self.hexLabel.setText('Hexadecimal Invalido')
                self.binLabel.setText('-')
                return None
        
        self.hexLabel.setText('0x' + hx)
        self.binLabel.setText('0b' + binary)
        
        return binary

    def update_combo_box(self):
        
        self.initialConditionComboBox.clear()
        
        t = self.code_f[self.codeComboBox.itemText(self.codeComboBox.currentIndex())][2]
        if(len(t) == 0):
            
            self.initialConditionLabel.hide()
            self.initialConditionComboBox.hide()
            return None
        
        for string in t:
            self.initialConditionComboBox.addItem('   ' +string)
        
        self.initialConditionLabel.show()
        self.initialConditionComboBox.show()

    def code_modified(self):
        
        self.update_combo_box()
        self.order_graph_update()

    def plot(self):        

        if(self.staticCheckBox.isChecked()): return None
        
        self.figure.clear()
        
        binary = self.read_bin_lineedit()
        
        if binary is None:
            self.canvas.draw()
            return None
        
        code_f_tuple = self.code_f[self.codeComboBox.itemText(self.codeComboBox.currentIndex())]
        
        binary_list = self.int_string_to_list(binary)
        if len(binary) % code_f_tuple[1]:
            binary_list = [0]*(code_f_tuple[1] - len(binary)%code_f_tuple[1]) + binary_list
        
        self.y = [ binary_list[0] ] + binary_list
        self.x = [ i for i in range(len(self.y)) ]

        if not self.hideGraphCheckBox.isChecked():

            self.apply_multiplier(self.y)

            self.ax = self.figure.add_subplot(211)
            self.ax.step(self.x, self.y)
            self.ax2 = self.figure.add_subplot(212)
        
        else:
            self.ax2 = self.figure.add_subplot(111)
        
        self.y2 = code_f_tuple[0](binary_list, self.initialConditionComboBox.currentIndex())
        self.y2 = [ self.y2[0] ] + self.y2
        self.x2 = [ i for i in range(len(self.y2)) ]
        
        self.apply_multiplier(self.y2)
        
        if(self.x[-1] != self.x2[-1]):
            mul = self.x[-1]/self.x2[-1]
            for i in range(len(self.x2)):
                self.x2[i] *= mul
                
        self.ax2.step(self.x2, self.y2)

        self.update_axis()

    def update_axis(self):

        if(self.ax2 is None): return None
    
        if(self.ax is not None): self.update_axis_partial(self.ax, self.x, self.y)
        self.update_axis_partial(self.ax2, self.x2, self.y2)
        
        self.canvas.draw()

    def update_axis_partial(self, ax, x, y):
        
        start = -x[-1]/20
        end = 21*x[-1]/20
        
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        
        ax.xaxis.grid(self.verticalGridCheckBox.isChecked())
        ax.yaxis.grid(self.horizontalGridCheckBox.isChecked())
        
        if(self.partialVizualizationCheckBox.isChecked() is True):
            value = (x[-1] - 19*self.VizualizationSpinBox.value()/20)*self.horizontalSlider.value()/99
            start = value - self.VizualizationSpinBox.value()/20
            end = start + 21*self.VizualizationSpinBox.value()/20
        
        diff = max(y) - min(y)
        ax.axis([start, end, min(y) - 0.2*diff - 0.04, max(y) + 0.2*diff + 0.04])
    
    def init_connect(self):
        
        self.horizontalSlider.valueChanged.connect(self.update_axis)
        self.lineEdit.textChanged.connect(self.order_graph_update)
        self.codeComboBox.currentIndexChanged.connect(self.code_modified)
        self.initialConditionComboBox.currentIndexChanged.connect(self.order_graph_update)
        self.partialVizualizationCheckBox.stateChanged.connect(self.partial_vizualization_state_changed)
        self.VizualizationSpinBox.valueChanged.connect(self.update_axis)
        self.outputMultiplierSpinBox.valueChanged.connect(self.plot)
        self.hideGraphCheckBox.stateChanged.connect(self.plot)
        self.stringInputRadioButton.clicked.connect(self.order_graph_update)
        self.hexInputRadioButton.clicked.connect(self.order_graph_update)
        self.binInputRadioButton.clicked.connect(self.order_graph_update)
        self.verticalGridCheckBox.stateChanged.connect(self.update_axis)
        self.horizontalGridCheckBox.stateChanged.connect(self.update_axis)
        self.staticCheckBox.stateChanged.connect(self.order_graph_update)
        self.actionSobre.triggered.connect(self.open_about)
        self.actionAjuda.triggered.connect(self.open_help)
        self.timer.timeout.connect(self.update_graph)

    def create_code_f_dict(self):
        
        self.code_f = { "Manchester Diferencial" : ( linecodes.generate_machester_differential, 1, ("Nivel Baixo", "Nivel Alto") ),
             "Manchester" : ( linecodes.generate_manchester, 1, () ),
             "B8ZS" : ( linecodes.generate_B8ZS, 1, ("Bit 1 Positivo", "Bit 1 Negativo") ),
             "NRZ Polar" : ( linecodes.generate_nrz_polar, 1, ()),
             "AMI" : ( linecodes.generate_ami, 1, ("Bit 1 Positivo", "Bit 1 Negativo")),
             "RZ" : ( linecodes.generate_rz, 1, () ),
             "2B1Q" : ( linecodes.generate_2B1Q, 2, () ),
             "MLT-3" : ( linecodes.generate_MLT3, 1, ("Bit 1", "Bit 0 Crescendo", "Bit 0 Decrescendo", "Bit -1") )}
        
        self.codeComboBox.clear()
        
        for code in self.code_f:
            self.codeComboBox.addItem(code)

    def create_graph(self):
        
        self.figure = plt.figure()
        
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        self.graphLayout.addWidget(self.canvas)
        self.graphLayout.addWidget(self.toolbar)

    def apply_multiplier(self, l):
        
        v = self.outputMultiplierSpinBox.value()
        
        for i in range(len(l)):
            l[i] *= v

    @staticmethod
    def hex_to_binary(hx):
        
        try:
            values = ""
            for v in hx:
                values += "{:0=4b}".format(int(v, 16))
            
        except ValueError:
            return None
        
        return values
    
    @staticmethod
    def bin_to_hex(binary):
        
        binary = '0'*(len(binary) % 4) + binary
        try:
            hx = ""
            for i in range(0, len(binary), 4):
                hx += '{:x}'.format(int(binary[i : i + 4], 2))
        
        except ValueError:
            return None
        
        return hx
    
    @staticmethod
    def word_to_hex(word):
        
        values = ''
        for letter in word:
            values += '{:2x}'.format(ord(letter))
            
        return values
    
    @staticmethod
    def int_string_to_list(string):
        
        return [int(i) for i in string]

    @staticmethod
    def open_about():
        About().exec_()
    
    @staticmethod
    def open_help():
        Help().exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())
