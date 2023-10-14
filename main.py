from config import APPID, APISecret, APIKey
if APPID == '' or APISecret == '' or APIKey == '':
    raise RuntimeError('请在cofig.py中输入讯飞开放平台语音识别服务API接口认证信息 https://www.xfyun.cn/')

import os
import sys, time, threading
import tkinter as tk
import ttkbootstrap as ttk
# from ttkbootstrap.constants import *
import tkinter.messagebox as mes
from record import Recorder
# from search import search_app_name
from recognition import Recognition
from tkinter import scrolledtext as scr
from match import get_closest_match, get_closest_app, get_closest_index
from volume import volume_control
from SysTrayIcon import SysTrayIcon
from voice import Voice
try:
    #raise ConnectionError
    from chat import chat
except:
    def chat(res):
        return '连接错误，无法使用聊天功能'
import time


Icon = None  # 判断是否打开系统托盘图标

# 弹幕函数(大段重复代码)
def top_text(text):
    global width, height
    if bs == 'big':
        tet.insert('end', text)
    else:
        a = tk.Tk()
        a.geometry('160x30+' + str(width) + '+' + str(height))
        height = height + 40
        a.overrideredirect(True)
        a.attributes('-alpha', 0.4)
        a.attributes('-topmost', True)
        tk.Label(a, text=text, font=('宋体', 13), foreground='white').pack(fill='both')
        def des(event):
            global height
            a.destroy()
            height = height - 40
        def gra():
            global height
            for i in range(70, 20, -5):
                a.attributes('-alpha', i/100)
                if i ==25:
                    height = height + 40
                    a.destroy()
                else:
                    time.sleep(1)
        added_thread_2 = threading.Thread(target=gra)
        added_thread_2.start()
        a.bind("<Double-Button-1>", des)
        a.mainloop()


window = tk.Tk()
window.title('Voice Recorder')
window.geometry('300x280')

# 浮窗function
g_p = 0
wh = 1
all_y = window.winfo_screenheight()
all_x = window.winfo_screenwidth()
x, y = 0, 0
rootalpha = 0.1
width = 1305
height = 320
is_hide = 'right'
bs = 'big'

# 首页title
ttk.Label(window, text='Voice Recorder', bootstyle='primary', font=('Arial',15)).pack()

# Text文本框
tet = scr.ScrolledText(window, width=35, height=5)
tet.place(x=10, y=25)

#  主界面移动函数
def get_pos(event):
    global x, y
    x, y = event.x, event.y
def window_move(event):
    global x, y, wh, g_p, bs
    if wh == 1:
        new_x = min(all_x - 160, (event.x - x) + window.winfo_x())
        new_y = min(all_y - 200, (event.y - y) + window.winfo_y())
        if new_x > 1150:
            if bs == 'big':
                # window.withdraw()
                def Hidden(icon='D:\\1.ico', hover_text="SysTrayIcon.py Demo", wh=wh):
                    global Icon
                    menu_options = ()
                    root.withdraw()  # 隐藏tk窗口
                    if not Icon: Icon = SysTrayIcon(
                        icon,
                        hover_text,
                        menu_options,
                        on_quit=exit,
                        tk_window=window,
                        wh=0,
                        bs=bs,
                        tk_window_small=window_small
                    )
                    Icon.activation()
                added_thread = threading.Thread(target=Hidden)
                added_thread.start()
                bs = 'small'
                window_small = tk.Toplevel()
                window_small.attributes('-topmost', True)
                window_small.geometry('200x60+1300+250')
                window_small.overrideredirect(True)
                def get_ps(event):
                    global x, y, g_p
                    x, y = event.x, event.y
                    # 初始形态
                    if g_p == 0:
                        window_small.geometry('200x60+1380+250')
                        g_p = 1
                    # 小窗口
                    else:
                        g_p = 0
                        window_small.geometry('200x60+1300+250')
                def ex(event):
                    global wh, bs
                    mes.showwarning(title='Warning', message='Back to the main model')
                    window_small.destroy()
                    wh = 1
                    bs = 'big'
                    window.deiconify()
                photo = tk.PhotoImage(file='iii.png')
                tk.Label(window_small, image=photo).place(x=0, y=0)
                ttk.Button(window_small, text='record', command=start_stop).place(x=75, y=18)
                window_small.bind("<Button-3>", get_ps)
                window_small.bind("<Double-Button-1>", ex)
                window_small.mainloop()
                wh = 0
        if new_x > -15 and new_y > -18 and new_y < 650:
            window.geometry('300x260+' + str(new_x) + '+' + str(new_y))
# 调透明度
def change_alpha(event):
    global rootalpha
    if rootalpha == 0.4:
        rootalpha = 0.8
    else:
        rootalpha = 0.4
        window.attributes('-alpha', rootalpha)


# bind functions to operation
window.bind("<B1-Motion>", window_move)
window.bind("<Button-1>", get_pos)
window.bind("<Double-Button-1>", change_alpha)


# ‘开始/停止’button
rec = Recorder()
reg = Recognition(APPID=APPID, APISecret=APISecret,
                          APIKey=APIKey)
voice = Voice(APPID=APPID, APISecret=APISecret,
                       APIKey=APIKey)


def send():
    while True:
        if rec._running and rec.frames:
            reg.frames.extend(rec.send_frames())
            #print(len(reg.frames))

def run_send():
    t = threading.Thread(target=send)
    t.setDaemon(True)
    t.start()
run_send()


status = -1      # -1:聊天  0:打开程序  0.5:程序-确认 1:调节音量
software, path = [], []


def start_stop():
    global status, software, path
    if rec._running:
        rec.start_stop()
        rec.reset()
        t = 0
        while not reg.result:
            # 请再说一次
            if t > 1:
                top_text('请再说一次' + '\n')
                voice.get_text('请再说一次')
                return
            t += 0.01
            time.sleep(0.01)
        print(reg.result)
        #reg.result = input('1:')
        if status != 0.5:
            status = get_closest_match(reg.result)
        print(status)
        if status == -1:
            r = chat(reg.result)
            top_text(r + '\n')
            voice.get_text(r)
        elif status == 0:
            software, path = get_closest_app(reg.result)
        #software, path = get_closest_match('微信')
        #print(get_closest_match('微信'))
            if len(software) == 1:
                top_text('打开' + software[0] + '\n')
                os.startfile(path[0])
                voice.get_text('打开' + software[0])
            else:
                r = '打开第几个？'
                top_text('打开第几个？')
                for i in range(len(software)):
                    top_text(str(i + 1) + '.' + software[i] + '\n')
                    r += str(i + 1) + '.' + software[i]
                voice.get_text(r)
                status = 0.5
        elif status == 0.5:
            status = -1
            index = get_closest_index(reg.result)
            top_text('打开' + software[index] + '\n')
            os.startfile(path[index])
            voice.get_text('打开' + software[index])
        elif status == 1:
            r = volume_control(reg.result)
            top_text(r + '\n')
            voice.get_text(r)
        elif status == 2:
            r = brightness_control(reg.result)
            tet.insert('end', r + '\n')
            voice.get_text(r)
        reg.result = ''


    else:
        rec.start_stop()
        reg.run_recognize()
ttk.Button(window, text='开始/停止录音', bootstyle='outline', command=start_stop).place(x=40, y=190)


# ‘退出’button
def out():
    mes.showwarning(title='Exit', message='Exiting...')
    window.destroy()
ttk.Button(window, text='退出', bootstyle='outline', command=out).place(x=190, y=190)

# 置顶函数：
top_if = 0
def toplevel():
    global top_if
    top_if ^= 1
    if top_if == 0:
        window.attributes('-topmost', 'false')
    elif top_if == 1:
        window.attributes('-topmost', 'true')
# checkbutton(置顶功能)
ttk.Checkbutton(window,text='置顶', bootstyle='default', command=toplevel).place(x=40, y= 160)


def Hidden_window(icon='D:\\1.ico', hover_text="SysTrayIcon.py Demo"):
    global Icon
    menu_options = ()
    root.withdraw()  # 隐藏tk窗口
    if not Icon: Icon = SysTrayIcon(
        icon,
        hover_text,
        menu_options,
        on_quit=exit,
        tk_window=root,
        wh=wh
    )
    Icon.activation()

def exit():
    mes.showwarning(title='Exit', message='Exiting...')
    root.destroy()

root = window
root.bind("<Unmap>",
          lambda event: Hidden_window() if root.state() == 'iconic' else False)
root.protocol('WM_DELETE_WINDOW', exit)
root.resizable()
root.mainloop()
