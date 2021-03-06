# -*- coding: utf-8 -*-
import sys
import shutil
import os.path
import datetime
import csv

from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel,  QPushButton, QSizePolicy,
    QComboBox, QApplication, QGridLayout, QProgressBar, QStyledItemDelegate, QLineEdit,
    QCalendarWidget, QFrame, QTableView, QVBoxLayout, QHeaderView, QHBoxLayout)
from PyQt5.QtGui import QColor, QStandardItemModel, QStandardItem, QRegExpValidator
from PyQt5.QtCore import (pyqtSlot, QObject, pyqtSignal, QThread, QDate, Qt,
                           QModelIndex, Q_ARG, QMetaObject, QRegExp)


from astrowork import aw_main_process
#import astroquery

UBUNTU = 'UBUNTU'
WIN = 'WIN'

SYSTEM = UBUNTU


if SYSTEM == UBUNTU:
    import appdirs
import six
import packaging
import packaging.version
import packaging.specifiers
import packaging.requirements



CATLISTDIR = './text/'
CATLISTFILE = 'catalogue.csv'
USERPARFILE = 'settings.csv'
DFLTPARFILE = 'default_parameters.csv'

# http://pyqt.sourceforge.net/Docs/PyQt4/qframe.html#Shadow-enum
_frameShape = QFrame.WinPanel
_frameShadow = QFrame.Sunken
_lineWidth = 3
_midLineWidth = 3

def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

def checkVmag(data):
    cols = len(data)
    if cols == 0:
        return -1
    [x, y] = data[0]
    for i in xrange(cols):
        if len(data[i]) != 2:
            return -1
        if not isinstance(data[i][1], (int, float)):
            return -1
        if (cols == 1) or (i == cols-1):
            if data[i][0] is not None:
                return -1
        else:
            if data[i][0] <= x:
                return -1
            if dara[i][1] >= y:
                return -1
        [x, y] = data[i]
    return 0
            
def saveVmag(data):
    lst = []
    with open(USERPARFILE, 'rb') as csvfile:
        fid = csv.DictReader(csvfile, delimiter=',', quotechar="'")
        for row in fid:
            row['vphi'] = str(data[row['code']]['vphi'])
            lst.append(row)
    with open(USERPARFILE, 'w') as csvfile:
        fields = lst[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fields, delimiter=',', quotechar="'")
        writer.writeheader()
        for row in lst:
            writer.writerow(row)
    return
    
class ValidatedItemDelegate(QStyledItemDelegate):
    def createEditor(self, widget, option, index):
        if not index.isValid():
            return 0
        string = index.data()
        #if ((string == u'<Не учитывается>') or
        #    (string.startswith('> '))):
        #    regExp = 
        #if ((index.column() == 0) and
        #    (index.row() == 0): #only on the cells in the first column
        editor = QLineEdit(widget)
        validator = QRegExpValidator(QRegExp("^[-+]?[0-9]*\.?[0-9]+$"), editor)
        editor.setValidator(validator)
        
        return editor
        #return super(ValidatedItemDelegate, self).createEditor(widget, option, index)

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
        
        self.settings_dirname = './'#CATLISTDIR
        self.settings_filename = USERPARFILE
        self.day_start = datetime.datetime.today()
        self.day_end = self.day_start + datetime.timedelta(days=1)
        self.mpf = 12
        
        chooseCatWgt = ChooseCatalogueList(self)
        self.layout.addWidget(chooseCatWgt, 0, 0, 1, 1)
        
        datein = DateInputW(self)
        self.layout.addWidget(datein, 1, 0, 1, 2)
        self.layout.addLayout(datein.layout, 1, 0, 1, 2)
        
        parameterWgt = ParameterList(self)
        self.layout.addWidget(parameterWgt, 0, 1, 1, 1)
        self.layout.addLayout(parameterWgt.layout, 0, 1, 1, 1)
        chooseCatWgt.connectExt(parameterWgt.updateInd)
        
        mainWork = MainProcess(self)
        self.layout.addWidget(mainWork, 2, 0, 1, 2)
        
        self.setGeometry(100, 100, 720, 480)
        self.setFixedSize(720, 480)
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
        
    def save_parameter(self, data):
        ncols = len(data)
        nrows = 2
        assert len(data[0]) == nrows
        for j in xrange(ncols):
            current = data[j]
            if j > 0:
                if (previous[0] >= current[0]):
                    data[j][0] = None
                    data = data[:j+1]
                    break
                if previous[1] <= current[1]:
                    data[j-1][0] = None
                    data = data[:j]
                    break
            previous = current
        
        lst = []
        ind = self.code_int
        code = self.flist[ind]['code']
        with open(USERPARFILE, 'rb') as csvfile:
            fid = csv.DictReader(csvfile, delimiter=',', quotechar="'")
            for row in fid:
                if row['code'] == code:
                    row['vphi'] = str(data)
                lst.append(row)
        with open(USERPARFILE, 'w') as csvfile:
            fields = lst[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fields, delimiter=',', quotechar="'")
            writer.writeheader()
            for row in lst:
                writer.writerow(row)
        
        return data

        
        
        
class ParameterList(QFrame):
    def __init__(self, parent):
        super(ParameterList, self).__init__() 
        self.parent = parent
        self.initUI()
        self.makeTable()
        self.makeButtons()
        
    def makeButtons(self):
        self.btn1 = QPushButton(u'Сохранить настройки', self)
        self.connectSave()
        self.btn2 = QPushButton(' + ', self)
        self.connectPlus()
        self.btn3 = QPushButton(' - ', self)
        self.connectMinus()
        
        self.dLayout.addWidget(self.btn1)
        self.dLayout.addWidget(self.btn2)
        self.dLayout.addWidget(self.btn3)
        
        self.layout.addLayout(self.dLayout)
        
    def makeTable(self):
        self.table = QTableView()
        minpol = QSizePolicy.Minimum
        self.table.setSizePolicy(minpol, minpol)
        self.table.setItemDelegate(ValidatedItemDelegate())
    
    
        self.updateInd(self.parent.code_int)
        self.table.setFixedSize(345, 100)
        self.layout.addWidget(self.table)
        
        #buttonParent = buttonPlusMinus()
        #buttonParent.makeButton(self)
        
    def getData(self):
        ncols = self.ncols
        nrows = 2
        data = []
        for j in xrange(ncols):
            tmp = []
            for i in xrange(nrows):
                index = self.model.index(i, j, QModelIndex())
                string = self.model.data(index)
                
                if ((string == u'<Не учитывается>') or
                   (string.startswith('> '))):
                    string = None
                else:
                    string = float(string)
                tmp.append( string )
            data.append(tmp)
        return data      
        
    def fillTable(self, data):
        self.ncols = len(data)
        self.model = QStandardItemModel(2, self.ncols, self)
        self.table.setModel(self.model)
        self.model.setVerticalHeaderLabels(['Vmag', 'Dist.'])
        self.data = data
        if self.ncols == 1:
            cont = u'<Не учитывается>'
    
        for j in xrange(len(data)):
            for i in xrange(len(data[j])):
                if data[j][i] is None:
                    if self.ncols == 1:
                        content = u'<Не учитывается>'
                    else:
                        content = '> ' + str(data[j-1][i])
                    item = QStandardItem(content)
                    item.setFlags((item.flags() & Qt.ItemIsEditable))
                else:
                    item = QStandardItem(str(data[j][i]))
                self.model.setItem(i, j, item)
                    
        self.table.resizeColumnsToContents()
        #sself.table.setColumnWidth(30, 20)
        self.table.resizeRowsToContents()
        vertheader = self.table.verticalHeader()
        vertheader.setSectionResizeMode(QHeaderView.Stretch)
        #horheader = self.table.horizontalHeader()
        #horheader.setSectionResizeMode(QHeaderView.Stretch)
        #self.table.horizontalHeader().setMinimumSectionSize(20)
    
     
    def updateInd(self, ind):
        code = self.parent.flist[ind]['code']
        data = eval(self.parent.dictpar[code]['vphi'])
        self.fillTable(data)
        
    def onActivatedPlus(self):        

        data = self.getData()
        if len(data) == 1:
            data[-1][0] = 0
        else:
            data[-1][0] = data[-2][0]
        new_element = [None, data[-1][1]]
        data.append(new_element)
        self.fillTable(data)
        #ind = self.parent.code_int
        #code = self.parent.flist[ind]['code']
        #self.parent.dictpar[code]['vphi'] = str(data)
        
    def connectPlus(self):
        self.btn2.clicked.connect(self.onActivatedPlus)
        
    def onActivatedMinus(self):
        if len(self.data) == 1:
            return        
        data = self.getData()
        data = data[:-1]
        data[-1][0] = None
        self.fillTable(data)
        #ind = self.parent.code_int
        #code = self.parent.flist[ind]['code']
        #self.parent.dictpar[code]['vphi'] = str(data)
        
    def connectMinus(self):
        self.btn3.clicked.connect(self.onActivatedMinus)
    
    def onActivatedSave(self):
        data = self.getData()
        ind = self.parent.code_int
        code = self.parent.flist[ind]['code']
        self.parent.dictpar[code]['vphi'] = str(data)
        data = self.parent.save_parameter(data)
        self.fillTable(data)
        
    def connectSave(self):
        self.btn1.clicked.connect(self.onActivatedSave)
        
        
    def initUI(self):
        self.layout = QVBoxLayout()
            
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor('white'))
        self.setPalette(palette)
        
        self.setFrameShape(_frameShape)
        self.setFrameShadow(_frameShadow)
        self.setLineWidth(_lineWidth)
        self.setMidLineWidth(_midLineWidth)
        
        self.dLayout = QHBoxLayout()

        
        return    
            

        
class DateInputW(QFrame):
    def __init__(self, parent):
        super(DateInputW, self).__init__()
        
        self.layout = QGridLayout()
        self.parent = parent
        
        self.title1 = QLabel(u'Начало:', self)
        self.title1.move(5, 5)
        self.cal1 = QCalendarWidget()
        self.cal1.setGridVisible(True)
        self.cal1.setDateEditEnabled(True)

        self.cal1.clicked.connect(self.setDateStart)
        if SYSTEM == UBUNTU:        
            self.cal1.setFixedSize(200, 160)
        elif SYSTEM == WIN:
            self.cal1.setFixedSize(250, 200)
        else:
            raise NotImplementedError
        ymd1 = [parent.day_start.year, parent.day_start.month, parent.day_start.day]
        qdate1 = QDate()
        qdate1.setDate(ymd1[0], ymd1[1], ymd1[2])
        self.cal1.setSelectedDate(qdate1)
        
        self.lbl1 = QLabel(self)
        self.lbl1.setText(parent.day_start.strftime('%d/%m/%Y'))
        self.lbl1.move(5, 25)
        
        self.title2 = QLabel(u'Конец:', self)
        self.title2.move(325, 5)
        self.cal2 = QCalendarWidget()
        self.cal2.setGridVisible(True)
        self.cal2.setDateEditEnabled(True)

        self.cal2.clicked.connect(self.setDateEnd)
        if SYSTEM == UBUNTU:        
            self.cal2.setFixedSize(200, 160)
        elif SYSTEM == WIN:
            self.cal2.setFixedSize(250, 200)
        else:
            raise NotImplementedError
        ymd2 = [parent.day_end.year, parent.day_end.month, parent.day_end.day]
        qdate2 = QDate()
        qdate2.setDate(ymd2[0], ymd2[1], ymd2[2])
        self.cal2.setSelectedDate(qdate2)
        
        self.lbl2 = QLabel(self)
        self.lbl2.setText(parent.day_end.strftime('%d/%m/%Y'))
        self.lbl2.move(325, 25)
        
        self.layout.addWidget(self.cal1, 1, 0)
        self.layout.addWidget(self.cal2, 1, 1)
        
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor('white'))
        self.setPalette(palette)
        
        self.setFrameShape(_frameShape)
        self.setFrameShadow(_frameShadow)
        self.setLineWidth(_lineWidth)
        self.setMidLineWidth(_midLineWidth)
        
        #change NavBar background color
        child = self.cal1.children()[3]
        palette = child.palette()
        palette.setColor(child.backgroundRole(), QColor('silver'))
        child.setPalette(palette)
        
        child = self.cal2.children()[3]
        palette = child.palette()
        palette.setColor(child.backgroundRole(), QColor('silver'))
        child.setPalette(palette)
        
        # change cell color
        brush = self.cal1.paintCell
        
        
        #self.cal1.setWeekdayTextFormat(headerForm)
        
       #parent.layout.addLayout(self.layout, 1, 0, 1, 2)
   
    def setDateStart(self):
        date = self.cal1.selectedDate()
        date = date.toPyDate()
        self.parent.day_start = datetime.datetime(date.year, date.month, date.day)
        self.lbl1.setText(self.parent.day_start.strftime('%d/%m/%Y'))
        
        minDate_dt = self.parent.day_start + datetime.timedelta(days=1)
        minDate = QDate()
        minDate.setDate(minDate_dt.year, minDate_dt.month, minDate_dt.day)
        self.cal2.setMinimumDate(minDate)

    def setDateEnd(self):
        date = self.cal2.selectedDate()
        date = date.toPyDate()
        self.parent.day_end = datetime.datetime(date.year, date.month, date.day)
        self.lbl2.setText(self.parent.day_end.strftime('%d/%m/%Y'))
        
        maxDate_dt = self.parent.day_end - datetime.timedelta(days=1)
        maxDate = QDate()
        maxDate.setDate(maxDate_dt.year, maxDate_dt.month, maxDate_dt.day)
        self.cal1.setMaximumDate(maxDate)
        

class Worker(QObject):
    finished = pyqtSignal()
    stoping = pyqtSignal()
    #message = pyqtSignal(str)
    
    def __init__(self):
        super(Worker, self).__init__()

    @pyqtSlot(object, object)
    def process(self, parent, pbar):
        print 'START'
        try:
            aw_main_process(parent.code,
                        parent.day_start,
                        parent.day_end,
                        parent.mpf,
                        directory=parent.settings_dirname,
                        filename=parent.settings_filename,
                        progressBar=pbar)
        #except astroquery.exceptions.TimeoutError:
            #self.message.emit('Timeout')
        #    pass
        except KeyboardInterrupt:
            pass
        finally:
            #self.message.emit('Unknown')
            pass
        print 'FINISHED'
        self.finished.emit()
        
    @pyqtSlot()
    def stop(self):
        self.stoping.emit()

class MyThread(QThread):
    def __init__(self):
        super(MyThread, self).__init__() 
        self.setTerminationEnabled(True)
       
        

class MainProcess(QFrame):
    def __init__(self, parent):
        super(MainProcess, self).__init__()
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(120, 40, 550, 25)
        
        self.doing = False
        self.btn = QPushButton(u'Старт', self)
        self.btn.move(20, 40)
        self.btn.clicked.connect(self.doAction)
        
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor('white'))
        self.setPalette(palette)
        
        self.setFrameShape(_frameShape)
        self.setFrameShadow(_frameShadow)
        self.setLineWidth(_lineWidth)
        self.setMidLineWidth(_midLineWidth)
        
    def doAction(self):
        if not self.doing:
            self.btn.setText(u'Стоп')
            self.thread = MyThread()
            self.pbar.setValue(0)
            self.worker = Worker()
            self.worker.moveToThread(self.thread)
            self.doing = True
            #self.thread.started.connect(self.worker.process)#worker.process)
            self.worker.finished.connect(self.thread.quit)
            #self.worker.finished.connect(self.worker.deleteLater)
            #self.worker.finished.connect(self.update_button)
            self.thread.finished.connect(self.update_button)
            #self.worker.stoping.connect(self.thread.terminate)
            #self.btn.clicked.connect(self.worker.stop)
            QMetaObject.invokeMethod(self.worker, 'process', Qt.QueuedConnection,
                                            Q_ARG(object, self.parent),
                                            Q_ARG(object, self.pbar))
                                            
            self.thread.start()
        else:
            #self.doing = False
            #self.btn.setText(u'Старт')
            self.thread.terminate()
            #self.pbar.setValue(0)
            pass

            
    def update_button(self):
        self.doing = False
        self.btn.setText(u'Старт')
        self.pbar.setValue(0)
        
            



class ChooseCatalogueList(QFrame):
    
    def __init__(self, parent):
        super(ChooseCatalogueList, self).__init__() 
        self.initUI(parent)
        
        
        #ChooseCatalogueList()
        
        
    def initUI(self, parent):    
        self.combo = QComboBox(self)
        self.title = QLabel(u'Выбор каталога:', self)
        self.lbl = QLabel('', self)
        self.descr = QLabel('', self)
        self.descr.setWordWrap(True)
        self.descr.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.onActivated(parent, parent.code_int)

        for x in parent.flist:
            self.combo.addItem(x['name'])
        
        self.combo.move(50, 50)
        self.title.move(5, 25)
        self.lbl.move(50, 100)
        self.descr.move(150, 50)
        
        def onact(ind):
            return self.onActivated(parent, ind)

        self.combo.activated[int].connect(onact) 
        
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor('white'))
        self.setPalette(palette)
         
        self.setFrameShape(_frameShape)
        self.setFrameShadow(_frameShadow)
        self.setLineWidth(_lineWidth)
        self.setMidLineWidth(_midLineWidth)
        
        self.setFixedSize(350, 120)
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
        
    def connectExt(self, fun):
        self.combo.activated[int].connect(fun)


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
