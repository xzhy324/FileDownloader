# Form implementation generated from reading ui file 'qtpainted.ui'
#
# Created by: PyQt6 UI code generator 6.2.3
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("FileDownloader")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(160, 60, 491, 141))
        self.textEdit.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)
        self.textEdit.setObjectName("textEdit")
        self.btn_inputFile = QtWidgets.QPushButton(self.centralwidget)
        self.btn_inputFile.setGeometry(QtCore.QRect(190, 230, 111, 41))
        self.btn_inputFile.setObjectName("btn_inputFile")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(90, 70, 72, 15))
        self.label.setObjectName("label")
        self.label2 = QtWidgets.QLabel(self.centralwidget)
        self.label2.setGeometry(QtCore.QRect(70, 320, 72, 15))
        self.label2.setObjectName("label2")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(160, 310, 491, 192))
        self.textBrowser.setObjectName("textBrowser")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(10, 0, 801, 16))
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.btn_ftp = QtWidgets.QPushButton(self.centralwidget)
        self.btn_ftp.setGeometry(QtCore.QRect(510, 230, 111, 41))
        self.btn_ftp.setObjectName("btn_ftp")
        self.btn_Download = QtWidgets.QPushButton(self.centralwidget)
        self.btn_Download.setGeometry(QtCore.QRect(350, 230, 111, 41))
        self.btn_Download.setObjectName("btn_Download")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen_Settings_txt = QtGui.QAction(MainWindow)
        self.actionOpen_Settings_txt.setObjectName("actionOpen_Settings_txt")
        self.menu.addAction(self.actionOpen_Settings_txt)
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        self.actionOpen_Settings_txt.triggered.connect(MainWindow.OpenSettingsFile)  # type: ignore
        self.btn_Download.clicked.connect(MainWindow.downloadFileClicked)  # type: ignore
        self.btn_inputFile.clicked.connect(MainWindow.inputFileClicked)  # type: ignore
        self.btn_ftp.clicked.connect(MainWindow.ftpClicked)  # type: ignore
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "FileDownloader"))
        self.btn_inputFile.setText(_translate("MainWindow", "Open File"))
        self.label.setText(_translate("MainWindow", "URL:"))
        self.label2.setText(_translate("MainWindow", "Status:"))
        self.btn_ftp.setText(_translate("MainWindow", "FTP Download"))
        self.btn_Download.setText(_translate("MainWindow", "HTTP(s) Download"))
        self.menu.setTitle(_translate("MainWindow", "FIle"))
        self.actionOpen_Settings_txt.setText(_translate("MainWindow", "Open Settings.txt"))
