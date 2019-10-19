import tkinter as tk
from utils.typedefs import Image_Type
from PIL import Image, ImageTk
from math import floor
from easygui import buttonbox as bb, choicebox as cb
from utils.gui_util import centerWindow

class ResizableCanvas(tk.Canvas):
    def __init__(self, master=None, image=None, cnf={}, **kw):
        super().__init__(master=master, cnf=cnf, **kw)
        self._orginalImage = image
        self.bind("<Configure>", lambda e:self._reRender())

    def setImage(self, image: Image_Type):
        self._orginalImage = image
        self._reRender()

    def _reRender(self):
        if not isinstance(self._orginalImage, Image_Type):
            print('reRenderCanvases was called while _orginalImage was not an image.')
            return
        c_size = (self.winfo_width(), self.winfo_height())
        img = Image.fromarray(self._orginalImage)
        fit_size = self._getImageFitSize(c_size, img.size)
        img = ImageTk.PhotoImage(img.resize(fit_size, Image.BICUBIC))
        self.delete("IMG")
        self.create_image(c_size[0]//2, c_size[1]//2,image=img,tags="IMG", anchor=tk.CENTER)
        # save image to self to prevent garbage collection
        self._resizedImage = img

    def _getImageFitSize(self, maxSize: tuple, curSize: tuple):
        ratio = curSize[0]/curSize[1]
        w, h = maxSize
        if w//ratio <= h:
            # max width fits
            return (w, floor(w/ratio))
        else:
            # max height fits
            return (floor(h*ratio), h)

def ynbox(msg="Shall I continue?", title=" ",
          choices=("[<Return>]Yes", "[<Escape>]No"), image=None,
          default_choice='[<Return>]Yes', cancel_choice='[<Escape>]No'):
        choice = bb(msg=msg, choices=choices, default_choice=default_choice, cancel_choice=cancel_choice, image=image, run=False)
        centerWindow(choice.ui.boxRoot)
        return choice.run()
def choicebox(msg="Pick an item", title="", choices=[], preselect=0,
              callback=None,
              run=True):
        ch = cb(msg,title,choices,preselect,callback,False)
        centerWindow(ch.ui.boxRoot)
        return ch.run()
