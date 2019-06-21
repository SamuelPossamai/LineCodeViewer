#!/usr/bin/env python3
'''
Module that contains the MainWindow class, a class to represent the LineCodeViewer window
if this file is executed, the LineCodeViewer program will be launched
'''

import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QTimer

from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from about import About
from help_dialog import Help

import linecodes

Ui_MainWindow, _ = uic.loadUiType("mainwindow.ui")

class LineCodeProperties:

    def __init__(self, code_function, min_bits, initial_condition_options):
        self._code_function = code_function
        self._min_bits = min_bits
        self._init_cond = initial_condition_options

    @property
    def code_function(self):
        return self._code_function

    @property
    def min_bits(self):
        return self._min_bits

    @property
    def init_cond_options(self):
        return self._init_cond

class MainWindow(QMainWindow, Ui_MainWindow):

    class _GraphsData:

        def __init__(self, n_graphs):
            self._data = [([], []) for i in range(n_graphs)]

        def set_values(self, x_values, y_values, n_graph=0):
            self._data[n_graph] = x_values, y_values

        def get_values(self, n_graph=0):
            return self._data[n_graph]

    def __init__(self, parent=None):

        QMainWindow.__init__(self, parent=parent)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self._first_axis = None
        self._second_axis = None
        self._third_axis = None

        self._graphs_data = MainWindow._GraphsData(3)

        self._timer = QTimer(self)

        self.horizontalSlider.hide()
        self.VizualizationSpinBox.hide()
        self.visibleBitsLabel.hide()
        self.initPosLabel.hide()

        self.create_graph()

        self._create_code_f_dict()
        self._init_connect()

        self.stringInputRadioButton.setChecked(True)

        self.lineEdit.setFocus()

        self._must_update_graph = 0

        self.update_combo_box()

        self._timer.setInterval(150)
        self._timer.start()

    def partial_vizualization_state_changed(self):

        self.horizontalSlider.setVisible(self.partialVizualizationCheckBox.isChecked())
        self.VizualizationSpinBox.setVisible(self.partialVizualizationCheckBox.isChecked())
        self.visibleBitsLabel.setVisible(self.partialVizualizationCheckBox.isChecked())
        self.initPosLabel.setVisible(self.partialVizualizationCheckBox.isChecked())
        self.update_axis()

    def _order_graph_update(self):

        self._must_update_graph = 1

    def update_graph(self):

        if self._must_update_graph == 2:
            self._must_update_graph = 0
            self.plot()

        elif self._must_update_graph >= 1:
            self._must_update_graph += 1

    def read_bin_lineedit(self):

        self._first_axis = None
        self._second_axis = None

        word = self.lineEdit.text()

        if not word:
            self.canvas.draw()
            self.hexLabel.setText('-')
            self.binLabel.setText('-')
            return None

        if self.binInputRadioButton.isChecked():

            binary = word

            if len(binary) > 2:
                if binary[0] == '0' and (binary[1] == 'b' or binary[1] == 'B'):
                    binary = binary[2:]

            hex_ = self._bin_to_hex(binary)

            if hex_ is None:
                self.canvas.draw()
                self.hexLabel.setText('-')
                self.binLabel.setText('Binário Invalido')
                return None

        else:

            if self.hexInputRadioButton.isChecked():
                hex_ = word
            else:
                hex_ = self._word_to_hex(word)

            if len(hex_) > 2:
                if hex_[0] == '0' and (hex_[1] == 'x' or hex_[1] == 'X'):
                    hex_ = hex_[2:]

            binary = self._hex_to_binary(hex_)

            if binary is None:
                self.canvas.draw()
                self.hexLabel.setText('Hexadecimal Invalido')
                self.binLabel.setText('-')
                return None

        self.hexLabel.setText('0x' + hex_)
        self.binLabel.setText('0b' + binary)

        return binary

    def update_combo_box(self):

        self.initialConditionComboBox.clear()

        c_prop = self._code_f[self.codeComboBox.itemText(self.codeComboBox.currentIndex())]
        init_options = c_prop.init_cond_options
        if not init_options:

            self.initialConditionLabel.hide()
            self.initialConditionComboBox.hide()
            return

        for string in init_options:
            self.initialConditionComboBox.addItem('   ' +string)

        self.initialConditionLabel.show()
        self.initialConditionComboBox.show()

    def code_modified(self):

        self.update_combo_box()
        self._order_graph_update()

    def plot(self):

        if self.staticCheckBox.isChecked():
            return

        self.figure.clear()

        binary = self.read_bin_lineedit()

        if binary is None:
            self.canvas.draw()
            return

        code_f_prop = self._code_f[self.codeComboBox.itemText(self.codeComboBox.currentIndex())]
        min_bits = code_f_prop.min_bits

        binary_list = [int(i) for i in binary]
        if len(binary) % min_bits:
            binary_list = [0]*(min_bits - len(binary) % min_bits) + binary_list

        y_values = [binary_list[0]] + binary_list
        x_values = [i for i in range(len(y_values))]

        self.VizualizationSpinBox.setMaximum(len(x_values) - 1)

        self._graphs_data.set_values(x_values, y_values)

        number_of_graphs = 1 + int(self.showInputCheckBox.isChecked()) + \
                           int(self.showClockCheckBox.isChecked())

        self.figure.subplots_adjust(hspace=0.8, left=0.05, right=0.95)

        if self.showInputCheckBox.isChecked():

            self.apply_multiplier(y_values)
            self.apply_offset(y_values)

            self._first_axis = self.figure.add_subplot(number_of_graphs, 1,
                                                       number_of_graphs - 1)
            self._first_axis.set_title('entrada')
            self._first_axis.step(x_values, y_values)

        if self.showClockCheckBox.isChecked():

            self._third_axis = self.figure.add_subplot(number_of_graphs, 1, 1)
            self._third_axis.set_title('clock')

            clock_x = [i/2 for i in range(2*len(y_values) - 1)]
            clock_y = [i%2 for i in range(2*len(y_values) - 1)]
            self._graphs_data.set_values(clock_x, clock_y, 2)
            self._third_axis.step(clock_x, clock_y)

        self._second_axis = self.figure.add_subplot(number_of_graphs, 1,
                                                    number_of_graphs)
        self._second_axis.set_title('saída')

        y_values_2 = code_f_prop.code_function(binary_list,
                                               self.initialConditionComboBox.currentIndex())
        y_values_2 = [y_values_2[0]] + y_values_2
        x_values_2 = [i for i in range(len(y_values_2))]

        self._graphs_data.set_values(x_values_2, y_values_2, 1)

        self.apply_multiplier(y_values_2)
        self.apply_offset(y_values_2)

        if x_values[-1] != x_values_2[-1]:
            mul = x_values[-1]/x_values_2[-1]
            for i, _ in enumerate(x_values_2):
                x_values_2[i] *= mul

        self._second_axis.step(x_values_2, y_values_2)

        self.update_axis()

    def update_axis(self):

        if self._second_axis is None:
            return

        s_x_values, s_y_values = self._graphs_data.get_values(1)
        if self._first_axis is not None:
            f_x_values, f_y_values = self._graphs_data.get_values()
            self.update_axis_partial(self._first_axis, f_x_values, f_y_values)
        if self._third_axis is not None:
            clock_x, clock_y = self._graphs_data.get_values(2)
            self.update_axis_partial(self._third_axis, clock_x, clock_y)
        self.update_axis_partial(self._second_axis, s_x_values, s_y_values)

        self.canvas.draw()

    def update_axis_partial(self, g_axis, x_values, y_values):

        start = -x_values[-1]/20
        end = 21*x_values[-1]/20

        g_axis.yaxis.set_major_locator(MaxNLocator(integer=True))
        g_axis.xaxis.set_major_locator(MaxNLocator(integer=True))

        g_axis.xaxis.grid(self.verticalGridCheckBox.isChecked())
        g_axis.yaxis.grid(self.horizontalGridCheckBox.isChecked())

        if self.partialVizualizationCheckBox.isChecked() is True:
            value = (x_values[-1] - 19*self.VizualizationSpinBox.value()/20) * \
                self.horizontalSlider.value()/99
            start = value - self.VizualizationSpinBox.value()/20
            end = start + 21*self.VizualizationSpinBox.value()/20

        first = y_values[0]
        for val in y_values:
            if val != first:
                break
        else:

            if first == 0:
                g_axis.axis([start, end, -0.24, 1.24])
            else:
                g_axis.axis([start, end, min(0, first) - 0.2*abs(first) - 0.04,
                             max(0, first) + 0.2*abs(first) + 0.04])

            return

        diff = max(y_values) - min(y_values)
        g_axis.axis([start, end, min(y_values) - 0.2*diff - 0.04, max(y_values) + 0.2*diff + 0.04])
        return


    def _init_connect(self):

        self.horizontalSlider.valueChanged.connect(self.update_axis)
        self.lineEdit.textChanged.connect(self._order_graph_update)
        self.codeComboBox.currentIndexChanged.connect(self.code_modified)
        self.initialConditionComboBox.currentIndexChanged.connect(self._order_graph_update)
        self.partialVizualizationCheckBox.stateChanged.connect(
            self.partial_vizualization_state_changed)
        self.VizualizationSpinBox.valueChanged.connect(self.update_axis)
        self.outputMultiplierSpinBox.valueChanged.connect(self.plot)
        self.offsetSpinBox.valueChanged.connect(self.plot)
        self.showInputCheckBox.stateChanged.connect(self.plot)
        self.showClockCheckBox.stateChanged.connect(self.plot)
        self.stringInputRadioButton.clicked.connect(self._order_graph_update)
        self.hexInputRadioButton.clicked.connect(self._order_graph_update)
        self.binInputRadioButton.clicked.connect(self._order_graph_update)
        self.verticalGridCheckBox.stateChanged.connect(self.update_axis)
        self.horizontalGridCheckBox.stateChanged.connect(self.update_axis)
        self.staticCheckBox.stateChanged.connect(self._order_graph_update)
        self.actionSobre.triggered.connect(self.open_about)
        self.actionAjuda.triggered.connect(self.open_help)
        self._timer.timeout.connect(self.update_graph)

    def _create_code_f_dict(self):

        LProp = LineCodeProperties

        self._code_f = {"NRZ Unipolar": LProp(linecodes.generate_nrz_unipolar, 1, ()),
                        "NRZ-L Polar": LProp(linecodes.generate_nrz_polar_l, 1, ()),
                        "NRZ-I Polar": LProp(linecodes.generate_nrz_polar_i,
                                             1, ("Nivel Baixo", "Nivel Alto")),
                        "RZ Polar": LProp(linecodes.generate_rz, 1, ()),
                        "Manchester": LProp(linecodes.generate_manchester, 1, ()),
                        "Manchester Diferencial":
                            LProp(linecodes.generate_machester_differential, 1,
                                  ("Nivel Baixo", "Nivel Alto")),
                        "B8ZS": LProp(linecodes.generate_b8zs, 1,
                                      ("Bit 1 Positivo", "Bit 1 Negativo")),
                        "AMI": LProp(linecodes.generate_ami, 1,
                                     ("Bit 1 Positivo", "Bit 1 Negativo")),
                        "Pseudoternario": LProp(linecodes.generate_pseudoternary,
                                                1, ("Bit 1 Positivo", "Bit 1 Negativo")),
                        "2B1Q": LProp(linecodes.generate_2b1q, 2, ()),
                        "MLT-3": LProp(linecodes.generate_mlt3, 1,
                                       ("Bit 1", "Bit 0 Crescendo",
                                        "Bit 0 Decrescendo", "Bit -1")),
                        "NRZ e 4B5B": LProp(linecodes.generate_nrz_4b5b, 4, ())}

        self.codeComboBox.clear()

        for code in self._code_f:
            self.codeComboBox.addItem(code)

    def create_graph(self):

        self.figure = plt.figure()

        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.graphLayout.addWidget(self.canvas)
        self.graphLayout.addWidget(self.toolbar)

    def apply_offset(self, values):

        offset = self.offsetSpinBox.value()

        for i, _ in enumerate(values):
            values[i] += offset

    def apply_multiplier(self, values):

        mul = self.outputMultiplierSpinBox.value()

        for i, _ in enumerate(values):
            values[i] *= mul

    @staticmethod
    def _hex_to_binary(hex_):

        try:
            values = ""
            for hex_char in hex_:
                values += "{:0=4b}".format(int(hex_char, 16))

        except ValueError:
            return None

        return values

    @staticmethod
    def _bin_to_hex(binary):

        binary = '0'*(len(binary) % 4) + binary
        try:
            hex_ = ""
            for i in range(0, len(binary), 4):
                hex_ += '{:x}'.format(int(binary[i : i + 4], 2))

        except ValueError:
            return None

        return hex_

    @staticmethod
    def _word_to_hex(word):

        values = ''
        for letter in word:
            values += '{:2x}'.format(ord(letter))

        return values

    @staticmethod
    def open_about():
        About().exec_()

    @staticmethod
    def open_help():
        Help().exec_()

def __runfile__():
    app = QApplication(sys.argv)

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    __runfile__()
