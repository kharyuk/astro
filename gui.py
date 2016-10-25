# -*- coding: utf-8 -*-
import sys
import csv
from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, 
    QComboBox, QApplication)

CATLISTDIR = './text/'
CATLISTFILE = './catalogue.csv'

class MainWindow(QMainWindow):
	def __init__(self, parent=None):
		super(MainWindow, self).__init__()

class ChooseCatalogueList(QWidget):
    
    def __init__(self):
        super(ChooseCatalogueList, self).__init__() 
        self.initUI()
        
        
        #ChooseCatalogueList()
        
        
    def initUI(self):    
        combo = QComboBox(self)
        
        self.flist = self.load_list()
        self.lbl = QLabel('', self)
        self.descr = QLabel('', self)
        self.descr.setWordWrap(True)
        self.onActivated(0)

        for x in self.flist:
			combo.addItem(x['name'])
		
        combo.move(50, 50)
        self.lbl.move(50, 150)
        self.descr.move(150, 50)

        combo.activated[int].connect(self.onActivated) 
         
        self.setGeometry(300, 300, 400, 200)
        self.setWindowTitle(u'Выбор каталога')
        self.show()
        
    def load_list(self):
    	flist = []
        with open(CATLISTDIR+CATLISTFILE, 'rb') as csvfile:
        	fid = csv.DictReader(csvfile, delimiter=',', quotechar="'")
        	for row in fid:
        		flist.append(row)
       	return flist
       	
    def onActivated(self, ind):
    	text = self.flist[ind]['fullname']
        self.lbl.setText(text)
        self.lbl.adjustSize()  
        
        text = self.flist[ind]['comment']
        self.descr.setText(text)
        self.descr.adjustSize()  


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = ChooseCatalogueList()
    sys.exit(app.exec_())
