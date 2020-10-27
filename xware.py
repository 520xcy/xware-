# -*- coding: utf-8 -*-
# @Date    : 2019-01-28 12:09:57
# @Author  : TsiayauHsiang (tsiayauhsiang@gmail.com)
# @Version : 0.1
# 
import os
import urllib.parse
import urllib.request
import json
import threading
import inspect
import ctypes
from time import ctime,sleep

ServerUrl = 'http://192.168.12.248'
ServerPort = '9000'
# Debug = True
Debug = False

def _async_raise(tid, exctype):
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
 
def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)

def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def del_task():
    taskid = int(input('输入任务ID:'))
    key = input('是否删除文件(y/N):').upper()
    deleteFile = 1 if key == 'Y' else 0
    url = ServerUrl + ':' + ServerPort + '/del?tasks=' + str(taskid) + '&v=2&deleteFile=' + str(deleteFile)
    if Debug: print(url)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        result = response.read().decode('utf-8')
        result = json.loads(urllib.parse.unquote(result))
    if Debug: print(result)
    for i, v in enumerate(result['tasks']):
        if v['result'] == 0:
            print('删除成功')
        elif v['result'] == 102434:
            print('任务不存在')
        else:
            print('删除失败' + str(v['result']))
    input()

def pasue_task():
    taskid = int(input('输入任务ID:'))
    url = ServerUrl + ':' + ServerPort + '/pause?tasks=' + str(taskid) + '&v=2'
    if Debug: print(url)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        result = response.read().decode('utf-8')
        result = json.loads(urllib.parse.unquote(result))
    if Debug: print(result)
    for i, v in enumerate(result['tasks']):
        if v['result'] == 0:
            print('暂停成功')
        elif v['result'] == 102434:
            print('任务不存在')
        elif v['result'] == 102436:
            print('无法暂停已暂停任务')
        else:
            print('操作失败' + str(v['result']))
    input()

def start_task():
    taskid = int(input('输入任务ID:'))
    url = ServerUrl + ':' + ServerPort + '/start?tasks=' + str(taskid) + '&v=2'
    if Debug: print(url)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        result = response.read().decode('utf-8')
        result = json.loads(urllib.parse.unquote(result))
    if Debug: print(result)
    for i, v in enumerate(result['tasks']):
        if v['result'] == 24579:
            print('开始下载成功')
        elif v['result'] == 102434:
            print('任务不存在')
        elif v['result'] == 102436:
            print('无法开始未暂停任务')
        else:
            print('操作失败' + str(v['result']))
    input()

def get_list(ListType):
    while True:
        clear()
        url = ServerUrl + ':' + ServerPort + '/list?v=2&type='+ ListType +'&pos=0&number=999999&needUrl=1&abs_path=1&fixed_id=0'
        if Debug: print(url)
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            result = json.loads(urllib.parse.unquote(result))
        if Debug: print(result)
        for i, v in enumerate(result['tasks']):
            if v['state'] == 0:
                state = '下载中'
            elif v['state'] == 9:
                state = '暂停'
            elif v['state'] == 11:
                state = '已完成'
            else:
                state = '错误' + str(v['state'])
            print('ID:' + str(v['id']) + ' 姓名:' + v['name'] + ' 进度:' + str(v['progress']/100) + ' 大小:%.2f' %(int(v['size'])/1024/1024/1024) + 'G ' + state + ' 速度:%.2f' %(v['speed']/1024) + 'KB/s')  
        print('===============================================================================================')
        print('0:暂停任务')
        print('1:开始任务')
        print('2:删除任务')
        print('9:返回')
        print('选择你需要做的操作:')
        sleep(2)

def show_list(ListType = '0'):
    while True:
        clear()
        ShowTimer = threading.Thread(target=get_list,args=(ListType))
        ShowTimer.setDaemon(True)
        ShowTimer.start()
        try:
            key = int(input())
            stop_thread(ShowTimer)
            if key == 0:
                pasue_task()
            elif key == 1:
                start_task()
            elif key == 2:
                del_task()
            elif key == 9:
                break
            else:
                raise ValueError
        except ValueError:
            input('输入错误!')
            stop_thread(ShowTimer)


def add_task():
    clear()
    TargetUrl = ServerUrl + ':' + ServerPort + '/boxSpace?v=2'
    if Debug: print(TargetUrl)
    req = urllib.request.Request(TargetUrl)
    with urllib.request.urlopen(req) as response:
        result = response.read().decode('utf-8')
        result = json.loads(urllib.parse.unquote(result))
    if Debug: print(result)
    driver = {}
    for i, v in enumerate(result['space']):
        driver[v['path']] = v['path'] + ":/TDDOWNLOAD/"
        print(v['path']+ ' %.2f' %(int(v['remain'])/1024/1024/1024) + 'G')
    while True:
        key = input('选择你的目标磁盘:').upper()
        if key in driver:
            break
    path = driver[key]
    while True:
        name = ''
        key = input('输入下载链接:')
        if len(key) == 0:
            continue
        url = key
        if key.startswith('magnet:'):
            if key.find('&dn=') == -1:
                name = 'unknown'
            else:
                name = urllib.parse.unquote(key[key.find('&dn=')+len('&dn='):len(key)])
            if key.find('&') != -1:
                url = key[0:key.find('&')]
        elif key.startswith('ed2k://'):
            splitArray = key.split('|')
            if len(splitArray) < 5:
                print('输入错误')
                continue
            try:
                name = urllib.parse.unquote(splitArray[2])
            except Exception as e:
                name = splitArray[2]

        if name == '':
            continue
        break
    tname = input('默认文件名:' + name + '\n不修改请留空:')
    name = urllib.parse.quote(name) if len(tname) == 0 else urllib.parse.quote(tname)
    url = urllib.parse.quote(url)
    path = urllib.parse.quote(path)
    TargetUrl = ServerUrl + ':' + ServerPort + '/createOne?v=2&type=1&url=' + url + '&path=' + path + '&name=' + name + '&fixed_id=1'
    if Debug: print(TargetUrl)
    req = urllib.request.Request(TargetUrl)
    print(req)
    with urllib.request.urlopen(req) as response:
        result = response.read().decode('utf-8')
        result = json.loads(urllib.parse.unquote(result))
    if Debug: print(result)
    if result['rtn'] == 0:
        print('添加成功')
    elif result['rtn'] == 202:
        print('任务已存在')
    elif result['rtn'] == 108545:
        print('链接错误')
    else:
        print('其它错误' + str(result['rtn']))
    input()

if __name__ == "__main__":
    while True:
        clear()
        url = ServerUrl + ':' + ServerPort + '/getsysinfo'
        if Debug: print(url)
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                result = response.read().decode('utf-8')
                result = json.loads(urllib.parse.unquote(result))
        except Exception as e:
            print(e)
            break
        if Debug: print(result)
        print('===============================================================================================')
        print('远程地址:' + ServerUrl + ':' + ServerPort + ' xware版本:' + str(result[6]) + ' 绑定用户:' + result[7])
        print('===============================================================================================')
        print('0:显示未完成列表')
        print('1:显示已完成列表')
        print('2:添加任务')
        print('9:退出')
        try:
            key = int(input('选择你需要做的操作:'))
            if key == 0:
                show_list()
            elif key == 1:
                show_list('1')
            elif key == 2:
                add_task()
            elif key == 9:
                break
            else:
                raise ValueError
        except ValueError:
            print('输入错误!')
