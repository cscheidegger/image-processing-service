# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'aeip.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import Application as appl

import os
import numpy as np

class AeIPGui(QtWidgets.QWidget):

    file_dialog = None
    dir_name = ""
    results = []

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)
        self.set_actions()

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(692, 109)
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(10, 10, 111, 41))
        self.pushButton.setObjectName("pushButton")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(140, 10, 141, 21))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(140, 40, 141, 21))
        self.label_3.setObjectName("label_3")
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.setGeometry(QtCore.QRect(440, 70, 101, 31))
        self.pushButton_2.setObjectName("pushButton_2")
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(260, 40, 421, 22))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(280, 10, 401, 22))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.pushButton_3 = QtWidgets.QPushButton(Form)
        self.pushButton_3.setEnabled(False)
        self.pushButton_3.setGeometry(QtCore.QRect(550, 70, 131, 31))
        self.pushButton_3.setObjectName("pushButton_3")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 80, 81, 16))
        self.label.setObjectName("label")
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setGeometry(QtCore.QRect(100, 80, 321, 16))
        self.label_4.setObjectName("label_4")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)


    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "AeIP Versão Desktop 1.0"))
        self.pushButton.setText(_translate("Form", "Abrir..."))
        self.label_2.setText(_translate("Form", "Diretório de Entrada:"))
        self.label_3.setText(_translate("Form", "Arquivo de Saída:"))
        self.pushButton_2.setText(_translate("Form", "Executar"))
        self.lineEdit.setText(_translate("Form", os.path.join(os.path.expanduser("~"), "resultados.txt")))
        self.pushButton_3.setText(_translate("Form", "Exportar Resultados"))
        #self.label.setText(_translate("Form", "Processando: "))
        #self.label_4.setText(_translate("Form", "IMG_0606.jpg..."))


    def set_actions(self):
        self.pushButton.clicked.connect(self.open_dir)
        self.pushButton_2.clicked.connect(self.run)
        self.pushButton_3.clicked.connect(self.export)


    def open_dir(self):
        self.file_dialog = QtWidgets.QFileDialog()
        self.file_dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        self.file_dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
        self.file_dialog.show()

        if self.file_dialog.exec_():
            self.dir_name = self.file_dialog.selectedFiles()[0]
            self.lineEdit_2.setText(self.dir_name)
            self.lineEdit.setText(os.path.join(self.dir_name, "resultados.csv"))
            self.pushButton_2.setEnabled(True)


    def update_status(self, proc, imname):
        self.label.setText(proc)
        self.label_4.setText(imname)
        QtWidgets.QApplication.processEvents()



    def export(self):
        out_type = self.lineEdit.text()[-4:]
        sep = ' '

        if out_type == '.csv':
            sep = ';'

        # Write file
        f = open(self.lineEdit.text(), 'w')

        header = np.array(['Nome da Imagem', 'Localização', 'Contagem Manual', 'Contagem AeIP', 'Descrição do Erro'])
        np.savetxt(f, np.array(header).reshape(1, -1), fmt="%s", delimiter=sep)

        for line in self.results:
            line = [str(x) for x in line]
            np.savetxt(f, np.array(line).reshape(1, -1), fmt="%s", delimiter=sep)

        f.close()



    def run(self):
        out_type = self.lineEdit.text()[-4:]

        if out_type != '.csv' and out_type != '.txt':
            QtWidgets.QMessageBox.warning(self, "Extensão do arquivo de saída.", "O arquivo deve conter extensão \".csv\" ou \".txt\".")
            return

        imnames = []

        for (dirpath, dirnames, filenames) in os.walk(self.dir_name):
            impath = filenames

        for path in impath:
            if path[-4:] == ".jpg" or path[-4:] == ".png":
                imnames.append(path)

        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)

        app = appl.Application()
        for image in imnames:
            lineres = []
            fullpath = os.path.join(self.dir_name, image)

            self.update_status("Processando:", image)

            pres = app.run(fullpath)

            lineres.append(image) # image name
            lineres.append("=HYPERLINK(\"" + str(fullpath) + "\")") # full image path
            lineres.append(" ") # Manual counting column

            # If atleast one egg was found..
            if isinstance(pres, int) == True:
                lineres.append(str(pres))
                lineres.append(" ") # Error message column

            else:
                lineres.append("0") # No eggs found
                lineres.append(pres) # Error message column

            self.results.append(lineres)

        self.pushButton_2.setEnabled(True)
        self.pushButton_3.setEnabled(True)
        self.update_status("", "")

        QtWidgets.QMessageBox.information(self, "Processamento Finalizado", "Processamento Finalizado.")