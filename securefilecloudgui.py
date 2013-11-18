import sys
from PyQt4 import QtGui


class SecureFileCloudGUI(QtGui.QWidget):
    
    def __init__(self):
        super(SecureFileCloudGUI, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        
	QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Secure File Cloud')
    
	btn = QtGui.QPushButton('Upload',self)
	btn.move(50,50)

        self.show()
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = SecureFileCloudGUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()    
