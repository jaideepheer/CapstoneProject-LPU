from gui.tkinter.processing_windows import VideoProcessingWindow
import tkinter as tk
from cv2 import imread, cvtColor, COLOR_BGR2RGB
import threading
import time

def func(delay):
    while(True):
        time.sleep(delay)
        print("sending data thread:", threading.get_ident())
        v.refreshProcessingData(img,img.copy(),img.copy())

root = tk.Tk()
v = VideoProcessingWindow(root, lambda:print("Paused"), lambda:print("Resumed"), lambda:print("Abort"))
img = cvtColor(imread("C:/Users/hp/Pictures/im.png"),COLOR_BGR2RGB)
v.refreshProcessingData(img,img.copy(),img.copy())
threading.Thread(target=func, args = (4,)).start()
root.mainloop()