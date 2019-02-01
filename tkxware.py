#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-01-28 12:09:57
# @Author  : TsiayauHsiang (tsiayauhsiang@gmail.com)
# @Version : 0.1
# coding=utf-8
#
import os
import tkinter as tk
from tkinter import messagebox,ttk,scrolledtext
import sys
import urllib.parse
import urllib.request
import json
import threading
import inspect
import ctypes
import time
from time import ctime,sleep


ServerUrl = 'http://192.168.12.248'
ServerPort = '9000'

Debug = False
#返回状态代码
ResCode = {
    0: '操作成功',
    202: '任务已存在',
    24579: '恢复下载成功',
    102434: '任务不存在',
    102436: '任务状态未改变',
    108545: '下载链接错误'
}
# 辅助代码
# 
# 


def handler_adaptor(fun, **kwds):
    """事件处理函数的适配器，相当于中介 handler_adaptor(函数名, 传参变量名 = 值, 传参变量名 = 值)"""
    return lambda event, fun=fun, kwds=kwds: fun(event, **kwds)

class MyException(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        if Debug: show_debug.print_debug('MyException:' + message)
        self.message = message

class UI:
    """docstring for Tools"""
    def get_screen_size(self, window):  
        return window.winfo_screenwidth(),window.winfo_screenheight()  
      
    def get_window_size(self, window):  
        return window.winfo_reqwidth(),window.winfo_reqheight()  
      
    def center_window(self, root, width, height):  
        screenwidth = root.winfo_screenwidth()  
        screenheight = root.winfo_screenheight()  
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)  
        root.geometry(size)  

    def cmdclear(self):
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

class Timer:

    def _async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")
     
    def stop_thread(self, thread):
        self._async_raise(thread.ident, SystemExit)



# Core代码
def get_list():
    while True:
        items = '未完成列表:\n' if ListType() == '0' else '已完成列表\n'
        url = '%s:%s/list?v=2&type=%s&pos=0&number=999999&needUrl=1&abs_path=1&fixed_id=0' % (ServerUrl, ServerPort, ListType())
        if Debug: show_debug.print_debug('[Url][%s] %s'%(sys._getframe().f_code.co_name, url))
        try:
            result = set_conn.conn(url)
            for i, v in enumerate(result['tasks']):
                if v['state'] == 0:
                    state = '下载中'
                elif v['state'] == 9:
                    state = '暂停'
                elif v['state'] == 11:
                    state = '已完成'
                else:
                    state = '错误' + str(v['state'])
                items += 'ID:%s 进度:%s 大小:%.2fG %s 速度:%.2f KB/s 任务名:%s \n' % (str(v['id']), str(v['progress']/100), (int(v['size'])/1024/1024/1024), state, int(v['speed'])/1024, v['name'])
            list_text.set(items)
        except Exception as e:
            tk.messagebox.showerror(title = '出错啦', message = e.message, parent = win_root)
            break;
        sleep(1)

def DebugType():
    global Debug
    Debug = bool(DebugVar.get())
    if Debug:
        show_debug.main()
    else:
        show_debug.exit()

def ListType():
    return str(SwitchType.get())
    
class DelTask():

    def main(self):
        self.root = tk.Toplevel()
        self.root.title('删除任务')
        ui.center_window(self.root, 385, 43)
        self.root.resizable(False, False)
        self.root.attributes("-topmost", 1)
        idL = tk.Label(self.root, 
        text='输入要删除任务的ID:',    # 标签的文字
        # font=('Arial', 9),     # 字体和字体大小
        width=20)
        idL.grid(row=1,column=1,padx=5,pady=5)

        self.id = tk.IntVar()
        idE = tk.Entry(self.root,
        # font=('Arial', 9),
        width=20,
        textvariable = self.id)
        idE.grid(row=1,column=2,padx=5,pady=5)


        submitB = tk.Button(self.root,
        text ="盘它",
        # font=('Arial', 9),
        width=5,
        # command = lambda:setServerPort(win_conn, win_conn_serE.get(), win_conn_portE.get()))
        command = self.submit)
        submitB.grid(row=1,column=3,padx=5,pady=5)


    def submit(self):
        ask = tk.messagebox.askyesnocancel('提示', '是否保留磁盘文件？', parent = self.root)
        if ask:
            deleteFile = '1'
        elif ask == None:
            return
        else:
            deleteFile = '0'
        try:
            url = '%s:%s/del?tasks=%s&v=2&deleteFile=%s' % (ServerUrl, ServerPort, str(self.id.get()), str(deleteFile))
            if Debug: show_debug.print_debug('[Url][%s] %s'%(self.__class__.__name__, url))
            result = set_conn.conn(url)
            for i, v in enumerate(result['tasks']):
                if v['result'] == 0:
                    tk.messagebox.showinfo('提示', '删除任务成功', parent=self.root)
                elif ResCode.get(v['result']) == None:
                    raise MyException('其它错误' + str(v['result']))
                else:
                    raise MyException(ResCode.get(v['result']))
        except Exception as e:
            tk.messagebox.showerror('出错啦', e.message, parent=self.root)

    def exit(self):
        self.win_conn.destroy()

class StartTask():

    def main(self):
        self.root = tk.Toplevel()
        self.root.title('开始任务')
        ui.center_window(self.root, 385, 43)
        self.root.resizable(False, False)
        self.root.attributes("-topmost", 1)
        idL = tk.Label(self.root, 
        text='输入要开始任务的ID:',    # 标签的文字
        # font=('Arial', 9),     # 字体和字体大小
        width=20)
        idL.grid(row=1,column=1,padx=5,pady=5)

        self.id = tk.IntVar()
        idE = tk.Entry(self.root,
        # font=('Arial', 9),
        width=20,
        textvariable = self.id)
        idE.grid(row=1,column=2,padx=5,pady=5)


        submitB = tk.Button(self.root,
        text ="盘它",
        # font=('Arial', 9),
        width=5,
        # command = lambda:setServerPort(win_conn, win_conn_serE.get(), win_conn_portE.get()))
        command = self.submit)
        submitB.grid(row=1,column=3,padx=5,pady=5)


    def submit(self):
        try:
            url = '%s:%s/start?tasks=%s&v=2' % (ServerUrl, ServerPort, str(self.id.get()))
            if Debug: show_debug.print_debug('[Url][%s] %s'%(self.__class__.__name__, url))
            result = set_conn.conn(url)
            for i, v in enumerate(result['tasks']):
                if v['result'] == 24579:
                    tk.messagebox.showinfo(title = '提示', message = '开始下载成功', parent=self.root)
                    self.exit()
                elif ResCode.get(v['result']) == None:
                    raise MyException('其它错误' + str(v['result']))
                else:
                    raise MyException(ResCode.get(v['result']))
        except Exception as e:
            tk.messagebox.showerror(title = '出错啦', message = e.message, parent=self.root)

    def exit(self):
        self.root.destroy()

class StopTask():

    def main(self):
        self.root = tk.Toplevel()
        self.root.title('暂停任务')
        ui.center_window(self.root, 385, 43)
        self.root.resizable(False, False)
        self.root.attributes("-topmost", 1)
        idL = tk.Label(self.root, 
        text='输入要暂停任务的ID:',    # 标签的文字
        # font=('Arial', 9),     # 字体和字体大小
        width=20)
        idL.grid(row=1,column=1,padx=5,pady=5)

        self.id = tk.IntVar()
        idE = tk.Entry(self.root,
        # font=('Arial', 9),
        width=20,
        textvariable = self.id)
        idE.grid(row=1,column=2,padx=5,pady=5)


        submitB = tk.Button(self.root,
        text ="盘它",
        # font=('Arial', 9),
        width=5,
        # command = lambda:setServerPort(win_conn, win_conn_serE.get(), win_conn_portE.get()))
        command = self.submit)
        submitB.grid(row=1,column=3,padx=5,pady=5)


    def submit(self):
        try:
            url = '%s:%s/pause?tasks=%s&v=2' % (ServerUrl, ServerPort, str(self.id.get()))
            if Debug: show_debug.print_debug('[Url][%s] %s'%(self.__class__.__name__, url))
            result = set_conn.conn(url)
            for i, v in enumerate(result['tasks']):
                if v['result'] == 0:
                    tk.messagebox.showinfo('提示', '暂停下载成功', parent=self.root)
                elif ResCode.get(v['result']) == None:
                    raise MyException('其它错误' + str(v['result']))
                else:
                    raise MyException(ResCode.get(v['result']))
        except Exception as e:
            tk.messagebox.showerror('出错啦', e.message, parent=self.root)

    def exit(self):
        self.win_conn.destroy()

class SetConn():
    def __init__(self):
        self.url = '%s:%s/getsysinfo' % (ServerUrl, ServerPort)
        if Debug: show_debug.print_debug('[Url][%s] %s'%(self.__class__.__name__, self.url))

    def main(self):
        self.root = tk.Tk()
        self.root.title('Xware链接参数')
        ui.center_window(self.root, 445, 43)
        self.root.resizable(False, False)
        self.root.attributes("-topmost", 1)
        self.root.protocol("WM_DELETE_WINDOW", exit)
        win_conn_serl = tk.Label(self.root, 
        text='服务器地址:',    # 标签的文字
        bg='green',     # 背景颜色
        # font=('Arial', 9),     # 字体和字体大小
        width=9)
        win_conn_serl.grid(row=1,column=1,padx=5,pady=5)

        win_conn_portl = tk.Label(self.root, 
        text='端口:',    # 标签的文字
        bg='red',     # 背景颜色
        # font=('Arial', 9),     # 字体和字体大小
        width=5)
        win_conn_portl.grid(row=1,column=3,padx=5,pady=5)
        self.server = tk.StringVar()
        win_conn_serE = tk.Entry(self.root,
        # font=('Arial', 9),
        width=20,
        textvariable = self.server)
        win_conn_serE.grid(row=1,column=2,padx=5,pady=5)
        self.port = tk.IntVar()
        win_conn_portE = tk.Entry(self.root,
        # font=('Arial', 9),
        width=5,
        textvariable = self.port)
        win_conn_portE.grid(row=1,column=4,padx=5,pady=5)

        win_conn_connB = tk.Button(self.root,
        text ="盘它",
        # font=('Arial', 9),
        width=5,
        # command = lambda:setServerPort(win_conn, win_conn_serE.get(), win_conn_portE.get()))
        command = self.submit)
        win_conn_connB.grid(row=1,column=5,padx=5,pady=5)
        exitB = tk.Button(self.root,
        text ="退出",
        # font=('Arial', 9),
        width=5,
        # command = lambda:setServerPort(win_conn, win_conn_serE.get(), win_conn_portE.get()))
        command = exit)
        exitB.grid(row=1,column=6,padx=5,pady=5)
        self.root.mainloop()

    def getXwareinfo(self):
        try:
            result = self.conn(self.url)
        except Exception as e:
            return False
        if Debug: show_debug.print_debug('[Result][%s] %s'%(self.__class__.__name__, result))
        return str(result[6]),result[7]

    def submit(self):
        try:
            if (not self.server.get().startswith('http://')) and (not self.server.get().startswith('https://')):
                raise MyException('服务器地址格式错误,请以http(s)://开头')
            elif self.port.get() < 1 or self.port.get() > 65535:
                raise MyException('端口错误,1-65535')
        except Exception as e:
            tk.messagebox.showerror(title = '出错啦', message = e.message, parent=self.root)
        else:
            global ServerUrl, ServerPort
            ServerUrl = self.server.get()
            ServerPort = str(self.port.get())
            self.url = '%s:%s/getsysinfo' % (ServerUrl, ServerPort)
            if self.getXwareinfo():
                tk.messagebox.showinfo('链接测试', '链接成功', parent=self.root)
                self.exit()
            elif tk.messagebox.askretrycancel(title='出错了', message='链接Xware服务器失败\n', parent=self.root) == False:
                exit()

    def conn(self, url):
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout = 1) as response:
                result = response.read().decode('utf-8')
                result = json.loads(urllib.parse.unquote(result))
            if Debug: show_debug.print_debug('[Result][%s] %s'%(self.__class__.__name__, result))
            return result
        except Exception as e:
            raise MyException(e)
            return False

    def exit(self):
        self.root.destroy()

class AddTask():
    def __init__(self):
        self.TargetUrl = '%s:%s/boxSpace?v=2' % (ServerUrl, ServerPort)
        if Debug: show_debug.print_debug('[Url][%s] %s'%(self.__class__.__name__, self.TargetUrl))

    def main(self):
        self.root = tk.Toplevel()
        self.root.title('Xware链接参数')
        # self.root.attributes('-alpha',0.8)
        ui.center_window(self.root, 500, 360)
        self.root.resizable(False, False)
        self.root.attributes("-topmost", 1)
        targetUrlL = tk.Label(self.root,
            text = '下载地址:')
        targetUrlL.grid(row = 2, column = 1, padx = 5, sticky = tk.W)
        
        self.targetUrl = tk.scrolledtext.ScrolledText(self.root, width = 67, height = 15)
        self.targetUrl.grid(row = 3, column = 1, columnspan = 2, padx = 5, pady = 5)
        clipboard_text = self.root.clipboard_get()
        if clipboard_text.startswith('magnet:') or clipboard_text.startswith('ed2k://') or clipboard_text.startswith('http://') or clipboard_text.startswith('https://'): self.targetUrl.insert(tk.INSERT, clipboard_text)
        self.rightmenu = tk.Menu(self.root,tearoff=0)
        self.rightmenu.add_command(label="复制", command = self.onCopy)
        self.rightmenu.add_command(label="粘贴", command = self.onPaste)
        self.rightmenu.add_separator()
        self.rightmenu.add_command(label="剪切", command = self.onCut)
        nameL = tk.Label(self.root,
            text = '文件名:')
        nameL.grid(row = 4, column = 1, padx = 5, pady = 5, sticky = tk.E)
        self.name = tk.StringVar()
        nameE = tk.Entry(self.root,
            width = 50,
            textvariable = self.name)
        nameE.grid(row = 4, column = 2, padx = 5, pady = 5)
        self.targetUrl.bind("<Button-3>", self.popupmenu)
        self.targetUrl.bind(sequence = '<FocusOut>', func = self.getName)
        self.subB = tk.Button(self.root, 
            text = '确定',
            width = 20,
            command = self.submit,
            state = 'disable')
        self.subB.grid(row = 5, column = 1, columnspan = 2, padx = 5, pady = 5)
        try:
            self.result = set_conn.conn(self.TargetUrl)
        except Exception as e:
            tk.messagebox.showerror(title='出错了', message='无法获取Xware磁盘信息\n' + str(e), parent=self.root)
            self.exit()
            return
        else:
            if Debug: show_debug.print_debug('[Result][%s] %s'%(self.__class__.__name__, self.result))
            deiverLabel = tk.Label(self.root, 
                text='选择目标磁盘:',    # 标签的文字
                # bg='green',     # 背景颜色
                # font=('Arial', 9),     # 字体和字体大小
                )
            deiverLabel.grid(row=1,column=1,padx=5,pady=5, sticky = tk.W)

            self.driverChosen = ttk.Combobox(self.root, width = 40, state='readonly')
            driver = []
            self.path = []
            for i, v in enumerate(self.result['space']):
                self.path.append(v['path'] + ':/TDDOWNLOAD/')
                driver.append(v['path'] + ' %.2fG' %(int(v['remain'])/1024/1024/1024))
            self.driverChosen['values'] = tuple(driver)
            self.driverChosen.grid(row=1, column=2, padx=5, pady=5)
            self.driverChosen.current(0)

    def submit(self):
        try:
            url = urllib.parse.quote(self.targetUrl.get('1.0', '1.end'))
            path = urllib.parse.quote(self.path[self.driverChosen.current()])
            name = urllib.parse.quote(self.name.get())
            if len(name) <= 0: raise MyException('文件名不能为空')
            TargetUrl = '%s:%s/createOne?v=2&type=1&url=%s&path=%s&name=%s&fixed_id=1' % (ServerUrl, ServerPort, url, path, name)
            if Debug: show_debug.print_debug('[Url][%s] %s'%(self.__class__.__name__, TargetUrl))
            result = set_conn.conn(TargetUrl)
            if result['rtn'] == 0:
                tk.messagebox.showinfo('提示', '添加成功', parent=self.root)
                self.exit()
            elif ResCode.get(result['rtn']) == None:
                raise MyException('其它错误' + str(result['rtn']))
            else:
                raise MyException(ResCode.get(result['rtn']))
        except Exception as e:
            tk.messagebox.showerror(title = '出错啦', message = e.message, parent=self.root)

    def getName(self, event):
        try:
            url = self.targetUrl.get('1.0', '1.end')
            if len(url) < 1: return #text即使空白也含有一个字符
            if url.startswith('magnet:'):
                if url.find('&dn=') == -1:
                    tname = 'unknown'
                else:
                    tname = urllib.parse.unquote(url[url.find('&dn=')+len('&dn='):len(url)])
                if url.find('&') != -1:
                    tname = url[0:url.find('&')]
            elif url.startswith('ed2k://'):
                splitArray = url.split('|')
                if len(splitArray) < 5:
                    raise MyException('输入错误')
                try:
                    tname = urllib.parse.unquote(splitArray[2])
                except Exception as e:
                    tname = splitArray[2]
            elif url.startswith('http://') or url.startswith('https://'):
                splitArray = url.split('/')
                tname = urllib.parse.unquote(splitArray[-1])
            else:
                raise MyException('下载链接需要以http(s)://,ed2k://,magnet:开头')
        except Exception as e:
            tk.messagebox.showerror(title = '出错啦', message = e.message, parent=self.root)
        else:
            self.name.set(tname)
            self.subB['state'] = 'normal'

    def popupmenu(self, event):
        self.rightmenu.post(event.x_root,event.y_root)

    def onCopy(self):
        try:
            text = self.targetUrl.get("sel.first", "sel.last")
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
        except Exception:
            pass

    def onPaste(self):
        try:
            text = self.root.clipboard_get()
            self.targetUrl.insert(tk.INSERT, text)
        except Exception:
            pass

    def onCut(self):
        self.onCopy()
        try:
            self.targetUrl.delete('sel.first', 'sel.last')
        except Exception:
            pass

    def exit(self):
        self.root.destroy()


class ShowDebug():
    """docstring for ShowDebug"""
    def __init__(self):
        self.int = 0

    def main(self):
        self.root = tk.Toplevel()
        self.root.title('Debug_Show')
        self.root.geometry('600x400')
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        self.msg = tk.scrolledtext.ScrolledText(self.root, width = 200, height = 100, wrap=tk.WORD)

        self.msg.pack()

    def print_debug(self, e):
        try:
            self.msg.config(state = tk.NORMAL)
            if self.int > 100:
                self.int = 0
                self.msg.delete('1.0', tk.END)
            self.int += 1
            self.msg.insert('1.0', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + e + '\n')
            
        except Exception as e:
            pass
        finally:
            self.msg.config(state = tk.DISABLED)
            pass

    def exit(self):
        global Debug
        DebugVar.set(0)
        Debug = False
        self.root.destroy()
    


if __name__ == "__main__":
    ui = UI()
    timer = Timer()
    add_task = AddTask()
    start_task = StartTask()
    stop_task = StopTask()
    del_task = DelTask()
    set_conn = SetConn()
    show_debug = ShowDebug()

    while True:
        xwareinfo = set_conn.getXwareinfo()
        if xwareinfo:
            break
        else:
            set_conn.main()

    win_root = tk.Tk()
    win_root.title('Xware远程地址:%s 端口:%s '% (ServerUrl, ServerPort) + 'xware版本:%s 绑定用户:%s' % xwareinfo)
    win_root.minsize(640, 400)  
    screenwidth = ui.get_screen_size(win_root)[0]
    screenheight = ui.get_screen_size(win_root)[1]
    ui.center_window(win_root, 800, screenheight*0.7)
    menubar = tk.Menu(win_root)
    #列表操作菜单
    SwitchType = tk.IntVar()
    menulist = tk.Menu(menubar, tearoff=False)
    menulist.add_radiobutton(label = '未完成', variable = SwitchType, value = '0')
    menulist.add_radiobutton(label = '已完成', variable = SwitchType, value = '1')
    menulist.add_separator()
    DebugVar = tk.IntVar()
    menulist.add_checkbutton(label = 'Debug', variable = DebugVar, command = DebugType)
    menubar.add_cascade(label = '查看列表', menu = menulist)
    #文件操作菜单
    controllist = tk.Menu(menubar, tearoff=False)
    controllist.add_command(label = '添加任务', command = add_task.main)
    controllist.add_separator()
    controllist.add_command(label = '开始任务', command = start_task.main)
    controllist.add_command(label = '暂停任务', command = stop_task.main)
    controllist.add_separator()
    controllist.add_command(label = '删除任务', command = del_task.main)
    menubar.add_cascade(label = '任务',menu = controllist)

    list_text = tk.StringVar()
    list_items = tk.Message(win_root,
    width=1000,
    textvariable = list_text)
    # list_items.pack(expand = tk.YES)  #居中
    list_items.pack()
    ListTimer = threading.Thread(target = get_list)
    ListTimer.setDaemon(True)
    ListTimer.start()
    win_root.config(menu = menubar)

    win_root.mainloop()
