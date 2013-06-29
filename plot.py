#!/usr/bin/env python

import serial
import threading
import time


from Tkinter import *

WIDTH = 600
HEIGHT = 400


class Plotter(Frame):

    def __init__(self, master=None):
        self.x = 0
        self.y = 0
        self.value = 0
        self.lines = []

        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def step(self):
        last_x = self.x
        last_y = self.y

        t = time.time() - start_time

        x = (t * 100)
        self.x = (t * 100) % WIDTH
        self.y = HEIGHT - (self.value / 1024.0) * HEIGHT
        #self.y += (x // WIDTH) * 30

        if last_x < self.x:
            line = self.draw.create_line(last_x, last_y, self.x, self.y)
            self.lines.append(line)
        while len(self.lines) > 2000:
            line = self.lines.pop(0)
            self.draw.delete(line)

        app.after(1, self.step)

    def createWidgets(self):

        self.draw = Canvas(self,
            width=WIDTH, height=HEIGHT,
            background="white"
        )
        # self.draw.create_rectangle(0, 0, "3.5i", "3.5i", fill="black")
        # self.draw.create_rectangle("10i", "10i", "13.5i", "13.5i", fill="blue")
        self.draw.pack({"side": "top"})

        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit

        self.QUIT.pack({"side": "left"})

root = Tk()
app = Plotter(master=root)

class Worker(threading.Thread):
    def __init__(self):
        super(Worker, self).__init__()
        self._stop = threading.Event()

    def run(self):
        while not self._stop.isSet():
            line = serial.readline()
            try:
                v = int(line)
            except ValueError:
                pass
            else:
                app.value = v

        print 'stopping'

    def stop(self):
        self._stop.set()

serial = serial.Serial('/dev/ttyACM0', 9600)

thread = Worker()
start_time = time.time()
thread.start()

app.after_idle(app.step)
app.mainloop()
thread.stop()
