from gui.tkinter.processing_windows import VideoProcessingWindow
from gui.tkinter.final_report_window import ReportWindow
from utils.gui_util import centerWindow
from utils.typedefs import AudioReport, VideoReport
import tkinter as tk
from cv2 import imread, cvtColor, COLOR_BGR2RGB
import threading
import time

root = tk.Tk()
r = ReportWindow(root,AudioReport(),VideoReport())
root.geometry("1024x600")
centerWindow(root)
root.mainloop()