from tkinter import *
import pyaudio
import time
import threading

class Recorder(Frame):
    def __init__(self, parent=None, chunk=2048, channels=1, rate=16000):
        Frame.__init__(self)
        self.parent = parent
        self.CHUNK = chunk
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = channels
        self.RATE = rate
        self._running = False
        self.frames = []
        self.starttime = 0
        self.elapsedtime = 0.0
        self.timer = None
        self.timestr = StringVar()  # 创建可变数据类型
        self.makeWidgets()
        self.flag = False

        p = pyaudio.PyAudio()
        self.stream = p.open(format=self.FORMAT,
                             channels=self.CHANNELS,
                             rate=self.RATE,
                             input=True,
                             frames_per_buffer=self.CHUNK)
        return

    def update(self):
        self.elapsedtime = time.time() - self.starttime
        self._setTime(self.elapsedtime)
        self.timer = self.after(50, self.update)

    def _setTime(self, elap):
        minutes = int(elap / 60)
        seconds = int(elap - minutes * 60.0)
        self.timestr.set('%.2d:%.2d' % (minutes, seconds))

    def makeWidgets(self):
        a = Label(self.parent, textvariable=self.timestr, font=10, height=5)
        self._setTime(self.elapsedtime)
        a.pack(fill='x', expand=1, pady=105, padx=105)

    def __recording(self):
        self._running = True
        print('recording')
        self.frames = []
        i = 0
        while self.flag:
            if self._running:
                data = self.stream.read(self.CHUNK)
                self.frames.append([i, data])
                i += 1
        data = self.stream.read(self.CHUNK)
        self.frames.append([-1, data])

    def start_stop(self):
        if self._running:
            self.after_cancel(self.timer)
            self.elapsedtime = time.time() - self.starttime
            self._setTime(self.elapsedtime)
            self._running = False
            print('stop')
        else:
            self.starttime = time.time() - self.elapsedtime
            self._running = True
            self.update()
            if not self.flag:
                self.flag = True
                t = threading.Thread(target=self.__recording)
                t.setDaemon(True)
                t.start()
            print('start')

    def reset(self):
        self.after_cancel(self.timer)
        self.starttime = time.time()
        self.elapsedtime = 0.0
        self._setTime(self.elapsedtime)
        self._running = False
        self.frames = []
        self.flag = False

    def send_frames(self):
        f = self.frames
        self.frames = []
        return f

    def get_record_audio(self):
        frames = []
        for i in range(0, int(self.RATE / self.CHUNK)):
            data = self.stream.read(self.CHUNK)
            frames.append(data)
        return frames
