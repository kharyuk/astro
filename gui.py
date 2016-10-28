# -*- coding: utf-8 -*-
import sys
import shutil
import os.path
import datetime
import csv
from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel,  QPushButton, QSizePolicy,
    QComboBox, QApplication, QGridLayout, QTableWidget, QTableWidgetItem, QProgressBar,
    QLineEdit, QFormLayout, QCalendarWidget)
from PyQt5.QtGui import QValidator
from PyQt5.QtCore import QBasicTimer, pyqtSlot, QProcess, QObject, pyqtSignal, QThread, QDate

from astrowork import aw_main_process
import astroquery

CATLISTDIR = './text/'
CATLISTFILE = 'catalogue.csv'
USERPARFILE = 'settings.csv'
DFLTPARFILE = 'default_parameters.csv'

def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        widget = QWidget(self)
        self.setCentralWidget(widget)
        self.layout = QGridLayout(widget)
        self.layout.setSpacing(10)
        
        self.flist = self.load_flist()
        self.code_int = 0
        self.code = self.flist[self.code_int]['code']
        
        self.dictpar = self.load_parameter()
        tmp_data=self.dictpar[self.code]['vphi']
        shape = [2, len(tmp_data)]
        
        self.settings_dirname = './'#CATLISTDIR
        self.settings_filename = USERPARFILE
        self.day_start = datetime.datetime.today()
        self.day_end = self.day_start + datetime.timedelta(days=10)
        self.mpf = 12
        
        chooseCatWgt = ChooseCatalogueList()
        chooseCatWgt.initUI(self)
        self.layout.addWidget(chooseCatWgt, 0, 0, 1, 1)
        
        datein = DateInputW(self)
        self.layout.addWidget(datein, 1, 0, 1, 2)
        self.layout.addLayout(datein.layout, 1, 0, 1, 2)
        
        parameterWgt = ParameterList(self)
        parameterWgt.makeVmagTable(self, tmp_data, shape)
        self.layout.addWidget(parameterWgt, 0, 1, 1, 1)
        
        mainWork = MainProcess(self)
        self.layout.addWidget(mainWork, 2, 0, 1, 2)
        
        #self.setLayout(layout)
        self.setGeometry(100, 100, 720, 480)
        self.setWindowTitle(u'Соединения Солнца и неподвижных объектов небесной сферы: расчёт')
        self.show()

    def load_flist(self):
        flist = []
        with open(CATLISTDIR+CATLISTFILE, 'rb') as csvfile:
            fid = csv.DictReader(csvfile, delimiter=',', quotechar="'")
            for row in fid:
                flist.append(row)
        return flist
        
    def load_parameter(self):
        exists = os.path.isfile(USERPARFILE)
        if not exists:
            shutil.copy(CATLISTDIR+DFLTPARFILE, USERPARFILE)
        dictpar = {}
        with open(USERPARFILE, 'rb') as csvfile:
            fid = csv.DictReader(csvfile, delimiter=',', quotechar="'")
            for row in fid:
                dictpar[row['code']] = removekey(row, 'code')
        return dictpar
        
class DateInputW(QWidget):
    def __init__(self, parent):
        super(DateInputW, self).__init__()
        
        self.layout = QGridLayout()
        self.parent = parent
        
        self.title1 = QLabel(u'Начало:', self)
        self.title1.move(0, 0)
        self.cal1 = QCalendarWidget()
        self.cal1.setGridVisible(True)
        self.cal1.setDateEditEnabled(True)

        self.cal1.clicked.connect(self.setDateStart)
        self.cal1.setFixedSize(200, 160)
        ymd1 = [parent.day_start.year, parent.day_start.month, parent.day_start.day]
        qdate1 = QDate()
        qdate1.setDate(ymd1[0], ymd1[1], ymd1[2])
        self.cal1.setSelectedDate(qdate1)
        
        self.lbl1 = QLabel(self)
        self.lbl1.setText(parent.day_start.strftime('%d/%m/%Y'))
        self.lbl1.move(0, 20)
        
        self.title2 = QLabel(u'Конец:', self)
        self.title2.move(320, 0)
        self.cal2 = QCalendarWidget()
        self.cal2.setGridVisible(True)
        self.cal2.setDateEditEnabled(True)

        self.cal2.clicked.connect(self.setDateEnd)
        self.cal2.setFixedSize(200, 160)
        ymd2 = [parent.day_end.year, parent.day_end.month, parent.day_end.day]
        qdate2 = QDate()
        qdate2.setDate(ymd2[0], ymd2[1], ymd2[2])
        self.cal2.setSelectedDate(qdate2)
        
        self.lbl2 = QLabel(self)
        self.lbl2.setText(parent.day_end.strftime('%d/%m/%Y'))
        self.lbl2.move(320, 20)
        
        self.layout.addWidget(self.cal1, 1, 0)
        self.layout.addWidget(self.cal2, 1, 1)
        
       #parent.layout.addLayout(self.layout, 1, 0, 1, 2)

        

        
    def setDateStart(self):
        date = self.cal1.selectedDate()
        date = date.toPyDate()
        self.parent.day_start = datetime.datetime(date.year, date.month, date.day)
        self.lbl1.setText(self.parent.day_start.strftime('%d/%m/%Y'))

    def setDateEnd(self):
        date = self.cal2.selectedDate()
        date = date.toPyDate()
        self.parent.day_end = datetime.datetime(date.year, date.month, date.day)
        self.lbl2.setText(self.parent.day_end.strftime('%d/%m/%Y'))
        

        

class Worker(QObject):
    finished = pyqtSignal()
    message = pyqtSignal(str)
    
    def __init__(self, parent, pbar):
        super(Worker, self).__init__()
        
        self.parent = parent
        self.pbar = pbar

    @pyqtSlot()
    def process(self):
        print 'START'
        try:
            aw_main_process(self.parent.code,
                        self.parent.day_start,
                        self.parent.day_end,
                        self.parent.mpf,
                        directory=self.parent.settings_dirname,
                        filename=self.parent.settings_filename,
                        progressBar=self.pbar)
        except astroquery.exceptions.TimeoutError:
            self.message.emit('Timeout')
        finally:
            self.message.emit('Unknown')
        print 'FINISHED'
        self.finished.emit()

class MainProcess(QWidget):
    def __init__(self, parent):
        super(MainProcess, self).__init__()
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(120, 40, 300, 25)
        
        self.doing = False
        self.btn = QPushButton(u'Старт', self)
        self.btn.move(20, 40)
        self.btn.clicked.connect(self.doAction)
        
    def doAction(self):
        if not self.doing:
            self.btn.setText(u'Стоп')
            self.thread = QThread(self)
            self.pbar.setValue(0)
            self.worker = Worker(self.parent, self.pbar)
            self.worker.moveToThread(self.thread)
            self.doing = True
            self.thread.started.connect(self.worker.process)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.finished.connect(self.update_button)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.setTerminationEnabled(True)
            self.thread.start()
        else:
            self.doing = False
            self.btn.setText(u'Старт')
            #self.thread.quit()
            self.thread.setTerminationEnabled(True)
            self.thread.terminate()
            
    def update_button(self):
        self.doing = False
        self.btn.setText(u'Старт')
        
            
class tableVmag(QWidget):
    def __init__(self):
        super(tableVmag, self).__init__()  

    def makeTable(self, parent, data, shape):
        [nrows, ncols] = shape
        self.tableMaker = QTableWidget(nrows, ncols)
        self.tableMaker.setVerticalHeaderLabels(['< v (Vmag)', ' < h (dist.)'])
        for j in xrange(len(data)):
            self.tableMaker.insertColumn(j)
            for i in xrange(len(data[j])):
                self.tableMaker.setItem(i, j, QTableWidgetItem(str(data[j][i])))
        self.tableMaker.setGeometry(50, 50, 100, 50)
        return self.tableMaker

class buttonPlusMinus(QWidget):
    def __init__(self):
        super(buttonPlusMinus, self).__init__()
    def makeButton(self, parent):
        buttonPlus = QPushButton('+', parent)
        buttonMinus = QPushButton('-', parent)
        #testBtn01.move(50, 450)

class ParameterList(QWidget):
    def __init__(self, parent):
        super(ParameterList, self).__init__() 
        self.parent = parent
        self.initUI()
        
    def makeVmagTable(self, parent, data, shape):
        self.tableVmag = tableVmag()
        self.readyTable = self.tableVmag.makeTable(parent, data, shape)
        
        buttonParent = buttonPlusMinus()
        buttonParent.makeButton(self)
        
        
    def initUI(self):
        return    
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
         
        #self.setGeometry(300, 300, 400, 200)
        #self.setWindowTitle(u'Выбор каталога')
        #self.show()
        


class ChooseCatalogueList(QWidget):
    
    def __init__(self):
        super(ChooseCatalogueList, self).__init__() 
        #self.initUI()
        
        
        #ChooseCatalogueList()
        
        
    def initUI(self, parent):    
        combo = QComboBox(self)
        self.title = QLabel(u'Выбор каталога:', self)
        self.lbl = QLabel('', self)
        self.descr = QLabel('', self)
        self.descr.setWordWrap(True)
        self.descr.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.onActivated(parent, parent.code_int)

        for x in parent.flist:
            combo.addItem(x['name'])
        
        combo.move(50, 50)
        self.title.move(0, 20)
        self.lbl.move(50, 100)
        self.descr.move(150, 50)
        
        def onact(ind):
            return self.onActivated(parent, ind)

        combo.activated[int].connect(onact) 
         
        #self.setGeometry(300, 300, 400, 200)
        #self.setWindowTitle(u'Выбор каталога')
        #self.show()
           
    def onActivated(self, parent, ind):
        text = parent.flist[ind]['fullname']
        self.lbl.setText(text)
        self.lbl.adjustSize()  
        
        text = parent.flist[ind]['comment']
        self.descr.setText(text)
        self.descr.adjustSize()
        
        parent.code_int = ind
        parent.code = parent.flist[ind]['code']


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
