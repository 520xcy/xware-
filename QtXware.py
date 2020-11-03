# -*- coding: utf-8 -*-
# @Date    : 2019-01-28 12:09:57
# @Author  : TsiayauHsiang (tsiayauhsiang@gmail.com)
# @Version : 0.1
#

import sys
from tkinter.constants import NO, YES
import urllib.parse
import urllib.request
import json
import threading
from datetime import datetime,timedelta
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Slot, qFastCos

DEBUG = False

ServerHost = 'http://192.168.12.248'
ServerPort = '9000'

Debug = False
# 返回状态代码
ResCode = {
    '0': u'操作成功',
    '202': u'任务已存在',
    '24579': u'恢复下载成功',
    '102434': u'任务不存在',
    '102436': u'任务状态未改变',
    '108545': u'下载链接错误'
}
StateCode = {
    '0': u'下载中',
    '9': u'暂停',
    '11': u'已完成'
}
# 辅助代码
#
#


def handler_adaptor(fun, **kwds):
    """事件处理函数的适配器，相当于中介 handler_adaptor(函数名, 传参变量名 = 值, 传参变量名 = 值)"""
    return lambda event, fun=fun, kwds=kwds: fun(event, **kwds)


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread = job_thread.start()

def currentTime():
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

class MyException(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


class NetWorking():
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def conn(self, url):
        req = urllib.request.Request(url)
        if debug.debugSW:
            data = QtWidgets.QTreeWidgetItem(debug.tree)
            data.setText(0, currentTime())
            data.setText(1, '发送')
            data.setText(2, url)
            data.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
        with urllib.request.urlopen(req, timeout=1) as response:
            result = response.read().decode('utf-8')
            result = json.loads(urllib.parse.unquote(result))
            if debug.debugSW:
                data = QtWidgets.QTreeWidgetItem(debug.tree)
                data.setText(0, currentTime())
                data.setText(1, '接受')
                data.setText(2, str(result))
                data.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
        return result

    def getXwareinfo(self, host, port):
        url = r'%s:%s/getsysinfo' % (host, port)
        try:
            result = self.conn(url)
        except Exception as e:
            return False
        else:
            text = u'服务器链接成功' if result else u'服务器链接失败'
            text += u' Xware远程地址:%s 端口:%s ' % (host, port) + u'xware版本:%s 绑定用户:%s' % (result[6], result[7])
            return text

    def getComplateList(self):

        url = r'%s:%s/list?v=2&type=1&pos=0&number=999999&needUrl=1&abs_path=1&fixed_id=0' % (
            self.host, self.port)
        # root.complatedata.clear()
        while root.complate.topLevelItemCount():
            item = QtWidgets.QTreeWidgetItem(root.complate.takeTopLevelItem(0))
            del item
        try:
            result = self.conn(url)
            for i, v in enumerate(result['tasks']):
                state = StateCode[str(v['state'])] if str(
                    v['state']) in StateCode else u'错误' + str(v['state'])
                items = QtWidgets.QTreeWidgetItem(root.complate)
                items.setText(0, str(v['id']))
                items.setText(1, v['name'])
                items.setText(2, state)
                items.setText(3, '%.2fG' % (int(v['size'])/1024/1024/1024))
                items.setText(4, str(timedelta(seconds=v['downTime'])))
                items.setText(5, datetime.fromtimestamp(v['createTime']).strftime('%Y-%m-%d %H:%M:%S'))
                items.setText(6, datetime.fromtimestamp(v['completeTime']).strftime('%Y-%m-%d %H:%M:%S'))
                # items = QtGui.QStandardItem(u'ID:%s 进度:%s 大小:%.2fG %s 速度:%.2f KB/s 任务名:%s' % (str(v['id']), str(
                #     v['progress']/100), (int(v['size'])/1024/1024/1024), state, int(v['speed'])/1024, v['name']))
                # root.complatedata.appendRow(items)
        except Exception as e:
            items = QtWidgets.QTreeWidgetItem(root.complate)
            items.setText(0,'')
            items.setText(1, u'数据返回错误')
            items.setText(2, str(e))

            # item = QtGui.QStandardItem(u'数据返回错误')
            # root.complatedata.appendRow(item)
            pass

    def getRunList(self):
        url = r'%s:%s/list?v=2&type=0&pos=0&number=999999&needUrl=1&abs_path=1&fixed_id=0' % (
            self.host, self.port)
        # items = ''
        while root.runlist.topLevelItemCount():
            item = QtWidgets.QTreeWidgetItem(root.runlist.takeTopLevelItem(0))
            del item
        try:
            result = self.conn(url)
            for i, v in enumerate(result['tasks']):
                # state = StateCode[str(v['state'])] if str(
                #     v['state']) in StateCode else u'错误' + str(v['state'])
                # items += u'ID:%s 进度:%s 大小:%.2fG %s 速度:%.2f KB/s 任务名:%s\n\r' % (str(v['id']), str(
                #     v['progress']/100), (int(v['size'])/1024/1024/1024), state, int(v['speed'])/1024, v['name'])
                items = QtWidgets.QTreeWidgetItem(root.runlist)
                items.setText(0, str(v['id']))
                items.setText(1, v['name'])
                items.setText(2, '%.2f' % (int(v['progress'])/100))
                items.setText(3, '%.2fG' % (int(v['size'])/1024/1024/1024))
                items.setText(4, datetime.fromtimestamp(v['createTime']).strftime('%Y-%m-%d %H:%M:%S'))
                items.setText(5, str(timedelta(seconds=v['downTime'])))
                items.setText(6, str(timedelta(seconds=int(v['remainTime']))))

        except Exception as e:
            # items = u'数据返回错误'
            items = QtWidgets.QTreeWidgetItem(root.complate)
            items.setText(0,'')
            items.setText(1, u'数据返回错误')
            items.setText(2, str(e))
            pass
        # root.runlist.setText(items)

        root.listTimer = threading.Timer(5, net.getRunList)
        root.listTimer.setDaemon(True)
        root.listTimer.start()

    def getDriverInfo(self):
        url = r'%s:%s/boxSpace?v=2' % (self.host, self.port)
        result = self.conn(url)
        return result

    def addTask(self, link, path, name):
        url = r'%s:%s/createOne?v=2&type=1&url=%s&path=%s&name=%s&fixed_id=1' % (
            self.host, self.port, link, path, name)
        result = self.conn(url)
        return result

    def pasueTask(self, id):
        url = r'%s:%s/pause?tasks=%s&v=2' % (self.host, self.port, str(id))
        result = self.conn(url)
        return result

    def startTask(self, id):
        url = r'%s:%s/start?tasks=%s&v=2' % (self.host, self.port, str(id))
        result = self.conn(url)
        return result

    def delTask(self, id, deleteFile):
        url = '%s:%s/del?tasks=%s&v=2&deleteFile=%s' % (
            self.host, self.port, str(id), str(deleteFile))
        result = self.conn(url)
        return result


class SetConn(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        # self.setParent(parent)
        self.setWindowTitle(u"设定链接参数")
        # self.setModal(True)

        self.hostinput = QtWidgets.QLineEdit(net.host)
        self.portinput = QtWidgets.QLineEdit(net.port)
        button = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, self)
        button.accepted.connect(self.submit)
        button.rejected.connect(self.reject)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.hostinput)
        layout.addWidget(self.portinput)
        layout.addWidget(button)

        self.setLayout(layout)

    def submit(self):
        thost = self.hostinput.text()
        tport = self.portinput.text()
        try:
            if (not thost.startswith('http://')) and (not thost.startswith('https://')):
                raise MyException(u'服务器地址格式错误,请以http(s)://开头')
            elif int(tport) < 1 or int(tport) > 65535:
                raise MyException(u'端口错误,1-65535')
        except MyException as e:
            msgbox.critical(self, u'出错啦', e.message)
        else:
            if net.getXwareinfo(thost, tport):
                net.host = thost
                net.port = tport
                msgbox.information(self, u'链接测试', u'链接成功')
                self.accept()
            else:
                msgbox.critical(self, u'出错了', u'链接Xware服务器失败\n')


class AddTask(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        driverconn = net.getDriverInfo()

        # self.setParent(parent)
        self.setWindowTitle(u'添加任务')
        # self.resize(500, 600)
        self.cb = QtWidgets.QApplication.clipboard()
        toplayout = QtWidgets.QHBoxLayout()
        driverlable = QtWidgets.QLabel(u'目标磁盘')
        driverlable.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.driver = QtWidgets.QComboBox()
        for i, v in enumerate(driverconn['space']):
            self.driver.addItem(
                v['path'] + ' %.2fG' % (int(v['remain'])/1024/1024/1024), v['path'] + ':/TDDOWNLOAD/')
        toplayout.addWidget(driverlable)
        toplayout.setStretchFactor(driverlable, 1)
        toplayout.addWidget(self.driver)
        toplayout.setStretchFactor(self.driver, 5)
        topbox = QtWidgets.QWidget()
        topbox.setLayout(toplayout)
        self.text = QtWidgets.QTextEdit(self)
        # self.text.adjustSize()
        self.text.setMinimumWidth(500)
        self.text.setAcceptRichText(False)
        self.text.textChanged.connect(self.setNewname)
        bottomlayout = QtWidgets.QHBoxLayout()
        filelable = QtWidgets.QLabel(u'保存文件名')
        filelable.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.newname = QtWidgets.QLineEdit(self)
        bottomlayout.addWidget(filelable)
        bottomlayout.setStretchFactor(filelable, 1)
        bottomlayout.addWidget(self.newname)
        bottomlayout.setStretchFactor(self.newname, 5)
        bottombox = QtWidgets.QWidget()
        bottombox.setLayout(bottomlayout)
        button = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, self)
        button.accepted.connect(self.submit)
        button.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(topbox)
        layout.addWidget(self.text)
        layout.addWidget(bottombox)
        layout.addWidget(button)
        clipboard = self.cb.text()
        if self.checkUrl(clipboard):
            self.text.setPlainText(clipboard)

        self.setLayout(layout)

    def submit(self):
        tname = self.getName()
        newname = self.newname.text()
        link = self.text.toPlainText()
        path = self.driver.currentData()
        try:
            if not tname:
                raise MyException(u'下载链接错误，需要以http(s)://,ed2k://,magnet:开头')
            if len(newname) < 1:
                newname = tname
            link = urllib.parse.quote(link)
            path = urllib.parse.quote(path)
            newname = urllib.parse.quote(newname)
            result = net.addTask(link, path, newname)
            if result['rtn'] == 0:
                msgbox.information(self, u'提示', u'添加成功')
                self.accept()
            elif result['rtn'] not in ResCode:
                raise MyException(u'其它错误' + str(result['rtn']))
            else:
                raise MyException(ResCode[str(result['rtn'])])
        except MyException as e:
            msgbox.critical(self, u'出错啦', e.message)

    def checkUrl(self, text):
        return (text.startswith('magnet:') or text.startswith('ed2k://') or text.startswith('http://') or text.startswith('https://'))

    def setNewname(self):
        text = self.getName()
        if text:
            self.newname.setText(text)
        else:
            self.newname.clear()

    def getName(self):
        text = self.text.toPlainText()
        if len(text) < 1:
            return  # text即使空白也含有一个字符
        if text.startswith('magnet:'):
            if text.find('&dn=') == -1:
                tname = 'unknown'
            else:
                tname = urllib.parse.unquote(
                    text[text.find('&dn=')+len('&dn='):len(text)])
            if text.find('&') != -1:
                tname = text[0:text.find('&')]
        elif text.startswith('ed2k://'):
            splitArray = text.split('|')
            if len(splitArray) < 5:
                return
            try:
                tname = urllib.parse.unquote(splitArray[2])
            except:
                tname = splitArray[2]
                pass
        elif text.startswith('http://') or text.startswith('https://'):
            splitArray = text.split('/')
            tname = urllib.parse.unquote(splitArray[-1])
        else:
            return
        return tname


class PasueTask(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        # self.setParent(parent)
        self.setWindowTitle(u"暂停任务")
        toplayout = QtWidgets.QHBoxLayout()
        lable = QtWidgets.QLabel(u'任务ID')
        lable.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.id = QtWidgets.QLineEdit()
        toplayout.addWidget(lable)
        toplayout.setStretchFactor(lable, 1)
        toplayout.addWidget(self.id)
        toplayout.setStretchFactor(self.id, 5)
        topbox = QtWidgets.QWidget()
        topbox.setLayout(toplayout)
        button = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, self)
        button.accepted.connect(self.submit)
        button.rejected.connect(self.reject)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(topbox)
        layout.addWidget(button)
        self.setLayout(layout)

    def submit(self):
        id = self.id.text()
        try:
            if len(id) < 1:
                raise MyException(u'id不能为空')
            result = net.pasueTask(id)
            code = str(result['tasks'][0]['result'])
            if code == '0':
                msgbox.information(self, u'提示', u'暂停下载成功')
                self.accept()
            elif code not in ResCode:
                raise MyException(u'其它错误' + code)
            else:
                raise MyException(ResCode[code])
        except MyException as e:
            msgbox.critical(self, u'出错啦', e.message)


class StartTask(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        # self.setParent(parent)
        self.setWindowTitle(u"开始任务")
        toplayout = QtWidgets.QHBoxLayout()
        lable = QtWidgets.QLabel(u'任务ID')
        lable.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.id = QtWidgets.QLineEdit()
        toplayout.addWidget(lable)
        toplayout.setStretchFactor(lable, 1)
        toplayout.addWidget(self.id)
        toplayout.setStretchFactor(self.id, 5)
        topbox = QtWidgets.QWidget()
        topbox.setLayout(toplayout)
        button = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, self)
        button.accepted.connect(self.submit)
        button.rejected.connect(self.reject)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(topbox)
        layout.addWidget(button)
        self.setLayout(layout)

    def submit(self):
        id = self.id.text()
        try:
            if len(id) < 1:
                raise MyException(u'id不能为空')
            result = net.startTask(id)
            code = str(result['tasks'][0]['result'])
            if code == '24579':
                msgbox.information(self, u'提示', u'开始下载成功')
                self.accept()
            elif code not in ResCode:
                raise MyException(u'其它错误' + code)
            else:
                raise MyException(ResCode[code])
        except MyException as e:
            msgbox.critical(self, u'出错啦', e.message)


class DelTask(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        # self.setParent(parent)
        self.setWindowTitle(u"删除任务")
        toplayout = QtWidgets.QHBoxLayout()
        lable = QtWidgets.QLabel(u'任务ID')
        lable.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.id = QtWidgets.QLineEdit()
        toplayout.addWidget(lable)
        toplayout.setStretchFactor(lable, 1)
        toplayout.addWidget(self.id)
        toplayout.setStretchFactor(self.id, 5)
        topbox = QtWidgets.QWidget()
        topbox.setLayout(toplayout)
        button = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, self)
        button.accepted.connect(self.submit)
        button.rejected.connect(self.reject)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(topbox)
        layout.addWidget(button)
        self.setLayout(layout)

    def submit(self):
        question = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Question, u'删除任务', u'是否要同时删除文件？', QtWidgets.QMessageBox.NoButton, self)
        yes_btn = question.addButton(u'删除文件', QtWidgets.QMessageBox.YesRole)
        no_btn = question.addButton(u'仅删除任务', QtWidgets.QMessageBox.NoRole)
        question.addButton(u'取消', QtWidgets.QMessageBox.RejectRole)
        question.exec_()
        if question.clickedButton() == yes_btn:
            deleteFile = 1
        elif question.clickedButton() == no_btn:
            deleteFile = 0
        else:
            return
        if root.delSubmit(self.id.text(), deleteFile):
            self.accept()
            net.getComplateList()



class App(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.state = False
        self.initUI()

    # 居中
    def center_window(self, widget):
        window = widget.window()
        window.setGeometry(
            QtWidgets.QStyle.alignedRect(
                QtCore.Qt.LeftToRight,
                QtCore.Qt.AlignCenter,
                window.size(),
                QtGui.QGuiApplication.primaryScreen().availableGeometry(),
            ),
        )

    @Slot()
    def switchDebug(self, action):
        debug.debugSW = action.data()
        if action.data():
            debug.show()
        else:
            debug.hide()

    @Slot()
    def switchState(self, action):
        self.stackedlayout.setCurrentIndex(int(action.data()))
        if action.data():
            net.getComplateList()

    @Slot()
    def setConn(self, checked):
        try:
            self.SetConn = SetConn()
            self.SetConn.exec()
            print(net.host, net.port)
        except Exception as e:
            msgbox.critical(self, u'出错啦', str(e))

    @Slot()
    def delete(self, checked):
        try:
            self.DelTask = DelTask()
            self.DelTask.exec()
        except Exception as e:
            msgbox.critical(self, u'出错啦', str(e))

    @Slot()
    def add(self, checked):
        try:
            self.AddTask = AddTask()
            self.AddTask.exec()
        except Exception as e:
            msgbox.critical(self, u'出错啦', str(e))

    @Slot()
    def pasue(self, checked):
        try:
            self.PasueTask = PasueTask()
            self.PasueTask.exec()
        except Exception as e:
            msgbox.critical(self, u'出错啦', str(e))

    @Slot()
    def start(self, checked):
        try:
            self.StartTask = StartTask()
            self.StartTask.exec()
        except Exception as e:
            msgbox.critical(self, u'出错啦', str(e))

    @Slot()
    def popDel(self):
        question = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Question, u'删除所选任务', u'是否要同时删除文件？', QtWidgets.QMessageBox.NoButton, self)
        yes_btn = question.addButton(u'删除所选文件', QtWidgets.QMessageBox.YesRole)
        no_btn = question.addButton(u'仅删除任务', QtWidgets.QMessageBox.NoRole)
        question.addButton(u'取消', QtWidgets.QMessageBox.RejectRole)
        question.exec_()
        if question.clickedButton() == yes_btn:
            deleteFile = 1
        elif question.clickedButton() == no_btn:
            deleteFile = 0
        else:
            return
        selectlist = self.complate.selectedItems()
        try:
            for select in selectlist:
                id = select.text(0)
                self.delSubmit(id, deleteFile, multiple=True)
        except Exception as e:
            msgbox.critical(self, u'出错啦', str(e))
        else:
            msgbox.information(self, u'提示', u'删除任务成功')
            net.getComplateList()


    def delSubmit(self, id, deleteFile, multiple = False):
        try:
            if len(id) < 1:
                raise MyException(u'id不能为空')
            result = net.delTask(id, deleteFile)
            code = str(result['tasks'][0]['result'])
            if code == '0': 
                if not multiple:
                    msgbox.information(self, u'提示', u'删除任务成功')
                    return True
            elif code not in ResCode:
                raise MyException(u'其它错误' + code)
            else:
                raise MyException(ResCode[code])
        except MyException as e:
            msgbox.critical(self, u'出错啦', e.message)

    def startTimer(self):
        self.listTimer = threading.Timer(1, net.getRunList)
        self.listTimer.setDaemon(True)
        self.listTimer.start()

    def cancelTimer(self):
        self.listTimer.cancel()

    def initMenu(self):
        menu = self.menuBar()
        # menu.resize(100,20)
        task = menu.addMenu(u'任务')

        addtask = task.addAction(u'添加任务')
        addtask.setToolTip(u'添加一个新的下载任务')
        addtask.setShortcut(QtCore.Qt.CTRL | QtCore.Qt.Key_N)
        addtask.triggered.connect(self.add)

        deltask = task.addAction(u'删除任务')
        deltask.setToolTip(u'删除一个已存在的任务')
        deltask.setShortcut(QtCore.Qt.CTRL | QtCore.Qt.Key_D)
        deltask.triggered.connect(self.delete)

        task.addSeparator()

        starttask = task.addAction(u'开始任务')
        starttask.setToolTip(u'启动一个未完成的任务')
        starttask.setShortcut(QtCore.Qt.CTRL | QtCore.Qt.Key_S)
        starttask.triggered.connect(self.start)

        pasuetask = task.addAction(u'暂停任务')
        pasuetask.setToolTip(u'暂停一个未完成的任务')
        pasuetask.setShortcut(QtCore.Qt.CTRL | QtCore.Qt.Key_P)
        pasuetask.triggered.connect(self.pasue)

        display = menu.addMenu(u'查看')
        displaygroup = QtWidgets.QActionGroup(display)

        discomplate = display.addAction(u'已完成')
        discomplate.setCheckable(True)
        discomplate.setToolTip(u'显示已完成任务列表')
        discomplate.setShortcut(QtCore.Qt.CTRL | QtCore.Qt.Key_C)
        discomplate.setData(True)
        disrun = display.addAction(u'未完成', checkable=True, checked=True, data=False)
        disrun.setCheckable(True)
        disrun.setChecked(True)
        disrun.setToolTip(u'显示正在进行任务列表')
        disrun.setShortcut(QtCore.Qt.CTRL | QtCore.Qt.Key_R)
        disrun.setData(False)

        display.addAction(disrun)
        display.addAction(discomplate)
        displaygroup.addAction(disrun)
        displaygroup.addAction(discomplate)

        # displaygroup.setExclusive(True)
        displaygroup.triggered.connect(self.switchState)

        #另一种QAction方法
        display.addSeparator()
        debug = display.addMenu('Debug')
        debuggroup = QtWidgets.QActionGroup(debug)
        self.debugon = QtWidgets.QAction('On',debug,checkable=True,data=True)
        self.debugoff = QtWidgets.QAction('Off',debug,checkable=True,checked=True,data=False)
        debug.addAction(self.debugon)
        debug.addAction(self.debugoff)
        debuggroup.addAction(self.debugon)
        debuggroup.addAction(self.debugoff)
        debuggroup.triggered.connect(self.switchDebug)

        option = menu.addMenu(u'设置')
        editconn = QtWidgets.QAction(u'设置链接',option,StatusTip='设置xware服务器地址和端口')
        editconn.setShortcut(QtCore.Qt.CTRL | QtCore.Qt.Key_S)
        editconn.triggered.connect(self.setConn)
        option.addAction(editconn)

        

    def initStatusBar(self):
        self.status = self.statusBar()
        r = str(net.getXwareinfo(net.host, net.port))
        self.status.showMessage(r)

    def initRunview(self):
        title = QtWidgets.QLabel()
        title.setText(u'未完成任务')
        title.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        # self.runlist = QtWidgets.QLabel()
        # self.runlist.setWordWrap(True)
        # self.runlist.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        self.runlist = QtWidgets.QTreeWidget()
        header = QtWidgets.QTreeWidgetItem([u'ID',u'任务名',u'状态',u'进度',u'大小',u'开始时间',u'已下载时间',u'剩余时间'])
        self.runlist.setHeaderItem(header)
        self.runlist.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(title)
        # layout.setStretchFactor(title, 1)

        layout.addWidget(self.runlist)
        # layout.setStretchFactor(self.runlist, 9)

        self.runlayout = QtWidgets.QWidget(self)
        self.runlayout.setLayout(layout)

    def initComplateview(self):

        title = QtWidgets.QLabel()
        title.setText(u'已完成任务')
        title.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        # complate = QtWidgets.QListView()

        # self.complatedata = QtGui.QStandardItemModel()
        # complate.setModel(self.complatedata)

        self.complate = QtWidgets.QTreeWidget()
        header = QtWidgets.QTreeWidgetItem([u'ID',u'任务名',u'大小',u'下载耗时',u'开始时间',u'完成时间'])
        self.complate.setHeaderItem(header)
        self.complate.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.complate.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.complate.customContextMenuRequested[QtCore.QPoint].connect(self.complateMenu)
        self.complate.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)


        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.complate)
        self.complatelayout = QtWidgets.QWidget(self)
        self.complatelayout.setLayout(layout)

    def complateMenu(self,event):
        popMenu = QtWidgets.QMenu(self)
        deltask = popMenu.addAction(u'删除', data=id)
        deltask.triggered.connect(self.popDel)
        popMenu.exec_(QtGui.QCursor.pos())

    def initStackedLayout(self):
        self.stackedlayout = QtWidgets.QStackedLayout()
        # self.stackedlayout.setStackingMode(QtWidgets.QStackedLayout.StackAll)
        self.stackedlayout.addWidget(self.runlayout)
        self.stackedlayout.addWidget(self.complatelayout)
        self.widget = QtWidgets.QWidget(self)
        self.widget.setLayout(self.stackedlayout)
        self.setCentralWidget(self.widget)
        
    def initUI(self):
        self.resize(800, 600)
        self.center_window(self)
        self.initRunview()
        self.initComplateview()
        self.initStackedLayout()
        self.initStatusBar()
        self.initMenu()

        self.setWindowTitle(u'Xware客户端')

        
        self.show()

class DebugWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.debugSW = False
        self.initUI()
    
    def initUI(self):
        self.resize(600, 600)
        self.setWindowTitle(u'Debug信息窗口')

        self.tree = QtWidgets.QTreeWidget()
        header = QtWidgets.QTreeWidgetItem(['时间','方向','数据'])
        self.tree.setHeaderItem(header)
        self.tree.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tree)
        self.setLayout(layout)

    def closeEvent(self, event):
        root.debugoff.setChecked(True)
        



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    msgbox = QtWidgets.QMessageBox()
    debug = DebugWindow()
    net = NetWorking(ServerHost, ServerPort)
    root = App()
    root.show()

    root.startTimer()
    net.getComplateList()

    sys.exit(app.exec_())
