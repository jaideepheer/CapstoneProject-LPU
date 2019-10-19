import tkinter as tk
from tkinter import messagebox as tk_msgbox
from gui.custom_subclasses import ResizableCanvas

class ProcessingWindow:
    def __init__(self, master: tk.Tk, pauseCallback=lambda:None, resumeCallback=lambda:None, abortCallback=lambda:None):
        self.master = master
        self.pauseCallback = pauseCallback
        self.resumeCallback = resumeCallback
        self.abortCallback = abortCallback
        self.data = None
        self.kwdata = None

        self.isPaused = False

        # Bind window close handlers
        master.bind("<<GracefullShutdown>>", lambda e:self._onGracefullShutdown())
        master.protocol("WM_DELETE_WINDOW", self.onAbortProcessing)
    
    def refreshProcessingData(self, *data, **kwdata):
        self.data = data
        self.kwdata = kwdata
        self.master.event_generate("<<RefreshProcessingData>>", when="tail")
    
    def onProcessingComplete(self):
        self.doGracefullShutdown()
    
    def onAbortProcessing(self):
        self.pauseProcessing()
        if tk_msgbox.askokcancel("Abort", "Do you want to stop processing?"):
            self._onGracefullShutdown()
        else:
            if self.isPaused:
                self.resumeProcessing()
    
    def pauseProcessing(self):
        if self.isPaused: return
        self.isPaused = True
        self.pauseCallback()
    
    def resumeProcessing(self):
        if not self.isPaused: return
        self.isPaused = False
        self.resumeCallback()
    
    def _onGracefullShutdown(self):
        try:
            self.pauseProcessing()
            self.abortCallback()
        except:
            pass
        finally:
            self.master.destroy()
    
    def doGracefullShutdown(self):
        self.master.event_generate("<<GracefullShutdown>>", when="tail")
    
class VideoProcessingWindow(ProcessingWindow):
    def __init__(self, master: tk.Tk, pauseCallback=lambda:None, resumeCallback=lambda:None, abortCallback=lambda:None):
        super().__init__(master, pauseCallback, resumeCallback, abortCallback)
        self.data = [None]*5
        fillStick = tk.W+tk.E+tk.N+tk.S

        self.frame = tk.Frame(master, relief=tk.SUNKEN, borderwidth=1, padx=5, pady=5)
        self.frame.grid(sticky=fillStick)

        # Fill internal frame
        self.canvasList = [ResizableCanvas(self.frame, background="#dde0da") for i in range(3)]
        self.canvasList[0].grid(row=1, column=0, sticky=fillStick)
        self.canvasList[1].grid(row=0, column=0, columnspan=2, sticky=fillStick)
        self.canvasList[2].grid(row=1, column=1, rowspan=2, sticky=fillStick)

        # Set internal frame grid weights
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=3)
        self.frame.rowconfigure(1, weight=1)

        # bind processing update handler
        master.bind("<<RefreshProcessingData>>", 
            lambda e: [self.canvasList[i].setImage(self.data[i]) for i in range(min(len(self.canvasList), len(self.data)))]
            )

        self.pause_button_text = tk.StringVar(self.frame, value="Pause")
        self.pause_button = tk.Button(
            master,
            textvariable=self.pause_button_text,
            command=self.onPauseButton
            )
        self.pause_button.grid(row=1, sticky=tk.E+tk.N+tk.S+tk.W, padx=5, pady=5)

        # set master grid weights
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.master.rowconfigure(1, minsize=50)
    
    def onPauseButton(self):
        if not self.isPaused:
            self.pauseProcessing()
            self.pause_button_text.set("Resume")
        else:
            self.resumeProcessing()
            self.pause_button_text.set("Pause")

#TODO: handle audio data and text transcript sent during processing data refresh
class AudioProcessingWindow(ProcessingWindow):
    def __init__(self, master: tk.Tk, pauseCallback=lambda:None, resumeCallback=lambda:None, abortCallback=lambda:None):
        super().__init__(master, pauseCallback, resumeCallback, abortCallback)
        self.data = [None]*5
        fillStick = tk.W+tk.E+tk.N+tk.S

        self.frame = tk.Frame(master, relief=tk.SUNKEN, borderwidth=1, padx=5, pady=5)
        self.frame.grid(sticky=fillStick)

        # Fill internal frame
        self.canvasList = [ResizableCanvas(self.frame, background="#dde0da") for i in range(2)]
        self.canvasList[0].grid(row=0, sticky=fillStick)
        self.canvasList[1].grid(row=1, sticky=fillStick)

        # Set internal frame grid weights
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        # bind processing update handler
        master.bind("<<RefreshProcessingData>>", 
            lambda e: [self.canvasList[i].setImage(self.data[i]) for i in range(min(len(self.canvasList), len(self.data)))]
            )

        self.pause_button_text = tk.StringVar(self.frame, value="Pause")
        self.pause_button = tk.Button(
            master,
            textvariable=self.pause_button_text,
            command=self.onPauseButton
            )
        self.pause_button.grid(row=1, sticky=tk.E+tk.N+tk.S+tk.W, padx=5, pady=5)

        # set master grid weights
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.master.rowconfigure(1, minsize=50)
    
    def onPauseButton(self):
        if not self.isPaused:
            self.pauseProcessing()
            self.pause_button_text.set("Resume")
        else:
            self.resumeProcessing()
            self.pause_button_text.set("Pause")
