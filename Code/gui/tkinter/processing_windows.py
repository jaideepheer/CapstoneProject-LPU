import tkinter as tk
from tkinter import messagebox as tk_msgbox
from PIL import Image, ImageTk
from utils.typedefs import Image_Type
from math import floor
from typing import List

class ProcessingWindow:
    def __init__(self, master: tk.Tk, pauseCallback=lambda:None, resumeCallback=lambda:None, abortCallback=lambda:None):
        self.master = master
        self.pauseCallback = pauseCallback
        self.resumeCallback = resumeCallback
        self.abortCallback = abortCallback
        self.__resized_images = []
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
    
    def reRenderCanvases(self, canvasList: List[tk.Canvas], imagesList: List[Image_Type]):
        # update all canvas to get size
        if imagesList == None or canvasList == None:
            print('reRenderCanvases was sent None argument.')
            return
        self.__resized_images.clear()
        canvas_size = [(c.winfo_width(), c.winfo_height()) for c in canvasList]
        # resize images to appropriate sizes
        for i in range(min(len(canvasList),len(imagesList))):
            if imagesList[i] is None: continue
            img = Image.fromarray(imagesList[i])
            fit_size = self._getImageFitSize(canvas_size[i], img.size)
            img = ImageTk.PhotoImage(img.resize(fit_size, Image.BICUBIC))
            # save images to self to prevent garbage collection
            self.__resized_images.append(img)
            # put images in canvas
            canvasList[i].delete("IMG")
            canvasList[i].create_image(canvas_size[i][0]//2, canvas_size[i][1]//2,image=img,tags="IMG", anchor=tk.CENTER)
    
    def _getImageFitSize(self, maxSize: tuple, curSize: tuple):
        ratio = curSize[0]/curSize[1]
        w, h = maxSize
        if w//ratio <= h:
            # max width fits
            return (w, floor(w/ratio))
        else:
            # max height fits
            return (floor(h*ratio), h)

class VideoProcessingWindow(ProcessingWindow):
    def __init__(self, master: tk.Tk, pauseCallback=lambda:None, resumeCallback=lambda:None, abortCallback=lambda:None):
        super().__init__(master, pauseCallback, resumeCallback, abortCallback)
        self.data = [None]*5
        fillStick = tk.W+tk.E+tk.N+tk.S

        self.frame = tk.Frame(master, relief=tk.SUNKEN, borderwidth=1, padx=5, pady=5)
        self.frame.grid(sticky=fillStick)

        # Fill internal frame
        self.canvasList = [tk.Canvas(self.frame, background="#dde0da") for i in range(3)]
        self.canvasList[0].grid(row=1, column=0, sticky=fillStick)
        self.canvasList[1].grid(row=0, column=0, columnspan=2, sticky=fillStick)
        self.canvasList[2].grid(row=1, column=1, rowspan=2, sticky=fillStick)

        # Set internal frame grid weights
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=3)
        self.frame.rowconfigure(1, weight=1)

        # bind resize and processing update handlers
        self.frame.bind("<Configure>", 
            lambda e:
                self.reRenderCanvases(self.canvasList, self.data)
            )
        master.bind("<<RefreshProcessingData>>", 
            lambda e:
                self.reRenderCanvases(self.canvasList, self.data)
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
        self.canvasList = [tk.Canvas(self.frame, background="#dde0da") for i in range(2)]
        self.canvasList[0].grid(row=0, sticky=fillStick)
        self.canvasList[1].grid(row=1, sticky=fillStick)

        # Set internal frame grid weights
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        # bind resize and processing update handlers
        self.frame.bind("<Configure>", 
            lambda e:
                self.reRenderCanvases(self.canvasList, self.data[2:])
            )
        master.bind("<<RefreshProcessingData>>", 
            lambda e:
                self.reRenderCanvases(self.canvasList, self.data[2:])
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
