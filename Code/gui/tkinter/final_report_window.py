import tkinter.ttk as ttk
import tkinter as tk
from gui.custom_subclasses import ResizableCanvas
from utils.typedefs import _GOLDEN_RATIO_INT_16BIT_, AudioReport, VideoReport

class ReportWindow:
    def __init__(self, master: tk.Tk, audioReport: AudioReport, videoReport: VideoReport):
        self.master = master
        self.shouldExit = True
        if not audioReport == None:
            self.audioImages = []

        # Create notebook for tabs
        fillStick = tk.W+tk.E+tk.N+tk.S
        self.notebook = ttk.Notebook(master)
        self.notebook.grid(row=0, columnspan=2, sticky=fillStick)
        # Create bottom button bar
        self.exit_btn = tk.Button(master, text="Exit", command=master.destroy)
        self.menu_btn = tk.Button(master, text="Main Menu", command=self.gotoMainMenu) # python is trash
        self.exit_btn.grid(row=1, column=0, sticky=fillStick, padx=5, pady=5)
        self.menu_btn.grid(row=1, column=1, sticky=fillStick, padx=5, pady=5)

        # Create video result frame
        if not videoReport == None:
            videoImages = [videoReport.videoThumbnail, videoReport.dominantEmotionFrame, videoReport.emotionRadarChart]
            videoSummary = [
                "Total Frames: %d"%videoReport.totalFramesProcessed,
                "Dominant Emotion: %s"%videoReport.dominantEmotion,
                "Total Face Frames: %d"%videoReport.totalFramesWithFace,
                "Face Occourance: %f %%"%(videoReport.totalFramesWithFace*100/videoReport.totalFramesProcessed,)
            ]
            videoFrame = tk.Frame(self.notebook, relief=tk.SUNKEN, borderwidth=1, padx=5, pady=5)
            # Fill video frame
            self.canvasList = [ResizableCanvas(videoFrame, image=videoImages[i], background="#dde0da") for i in range(3)]
            self.canvasList[0].grid(row=0, column=0, columnspan=2, sticky=fillStick)
            self.canvasList[1].grid(row=1, column=0, sticky=fillStick)
            self.canvasList[2].grid(row=2, column=0, sticky=fillStick)
            videoLog = tk.Listbox(videoFrame)
            for l in videoSummary: videoLog.insert(0,l)
            videoLog.grid(row=1, rowspan=2, column=1, sticky=fillStick)
            self.videoLog = videoLog

            # Set internal frame grid weights using golden ratio
            videoFrame.columnconfigure(0, weight=_GOLDEN_RATIO_INT_16BIT_[0])
            videoFrame.columnconfigure(1, weight=_GOLDEN_RATIO_INT_16BIT_[1])
            videoFrame.rowconfigure(0, weight=_GOLDEN_RATIO_INT_16BIT_[0]*2)
            videoFrame.rowconfigure(1, weight=_GOLDEN_RATIO_INT_16BIT_[1])
            videoFrame.rowconfigure(2, weight=_GOLDEN_RATIO_INT_16BIT_[1])
            
            # add frame to notebook
            self.notebook.add(videoFrame, text="Video Results")
            self.videoFrame = videoFrame # prevent garbage collection
        
        # Create audio result frame
        if not audioReport == None:
            audioImages = [audioReport.sentimentGraph, audioReport.wordCountBarChart]
            audioSummary = [
                "Total Words: %d"%audioReport.totalWords,
                "Total Time Processed: %f seconds"%audioReport.totalTimeProcessedSec,
                "Speed: %f words/sec"%audioReport.wordsPerSecond
            ]
            audioFrame = tk.Frame(self.notebook, relief=tk.SUNKEN, borderwidth=1, padx=5, pady=5)
            # Fill video frame
            self.canvasList = [ResizableCanvas(audioFrame, image=audioImages[i], background="#dde0da") for i in range(2)]
            self.canvasList[0].grid(row=0, column=0, sticky=fillStick)
            self.canvasList[1].grid(row=1, column=0, sticky=fillStick)
            audioLog = tk.Listbox(audioFrame)
            for l in audioSummary: audioLog.insert(0,l)
            audioLog.grid(row=0, rowspan=2, column=1, sticky=fillStick)
            self.videoLog = audioLog

            # Set internal frame grid weights using golden ratio
            audioFrame.columnconfigure(0, weight=_GOLDEN_RATIO_INT_16BIT_[1])
            audioFrame.columnconfigure(1, weight=_GOLDEN_RATIO_INT_16BIT_[0])
            audioFrame.rowconfigure(0, weight=1)
            audioFrame.rowconfigure(1, weight=1)
            
            # add frame to notebook
            self.notebook.add(audioFrame, text="Audio Results")
            self.audioFrame = audioFrame # prevent garbage collection

        # set master grid weights
        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.master.rowconfigure(1, minsize=50)
    
    def didUserChooseExit(self):
        return self.shouldExit
    
    # this is why python is trash
    def gotoMainMenu(self):
        self.shouldExit = False
        self.master.destroy()
