from pipedefs.core_pipes import PushPipe
from utils.typedefs import Image_Type
from typing import List, Union, Tuple
from typing_extensions import Literal, Callable
from gui.charts import radar_factory
from dataclasses import dataclass
import matplotlib.pyplot as plt
import numpy as np
class RadarChartRenderPipe(PushPipe[List[float], Image_Type]):
    @dataclass
    class RadarChartConfig():
        labels: Tuple
        title: str = "Emotion Chart"
        frame: Union[Literal['circle'],Literal['polygon']] = 'circle'
        figure_size: Tuple[int, int] = (4, 3)
    def __init__(self, config: RadarChartConfig, showWindow = False, postProcessCallback=None):
        super().__init__(postProcessCallback=postProcessCallback)
        N = len(config.labels)
        theta = radar_factory(N, config.frame)
        self.figure, axes = plt.subplots(figsize=config.figure_size, subplot_kw=dict(projection='radar_%d'%(N)))
        self.figure.subplots_adjust(top=0.82, bottom=0.06)
        axes.set_rgrids([0.2, 0.4, 0.6, 0.8])
        axes.set_ylim([0, 1])
        axes.set_title(config.title,  position=(0.5, 1.1), ha='center')
        axes.set_varlabels(config.labels)
        self.line, = axes.plot(theta, [0]*N)
        if showWindow:
            plt.ion()
            plt.show()
    def process(self, data: List[float], passThrough: PushPipe.PassThrough) -> Image_Type:
        data.append(data[0])    # make data circular
        data = np.asarray(data)
        self.line.set_ydata(data)
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        width, height = map(int, self.figure.get_size_inches() * self.figure.get_dpi())
        return np.fromstring(self.figure.canvas.tostring_rgb(), dtype='uint8').reshape(height, width, 3)

class BarChartSequentialRenderPipe(PushPipe[float, Image_Type]):
    @dataclass
    class BarChartConfig():
        xlabel: str
        ylabel: str
        title: str = "Word Counts"
        aspect_ratio: float = 1
        figure_scale: float = 1
        post_init: Callable[[plt.Figure,plt.Axes],None] = lambda fig, ax: None
        add_bar: Callable[[float, PushPipe.PassThrough, 'BarChartSequentialRenderPipe'],None] = (
            lambda data, pthru, self: self.axes.bar(self.x_val, data)
        )

    def __init__(self, config: BarChartConfig, x_init: float = 1, x_incr: float = 1, showWindow = False, postProcessCallback=None):
        super().__init__(postProcessCallback=postProcessCallback)
        self.figure, self.axes = plt.subplots(figsize=(config.figure_scale*config.aspect_ratio, config.figure_scale))
        # add title
        self.figure.subplots_adjust(top=0.82, bottom=0.06)
        self.axes.set_title(config.title,  position=(0.5, 1.1), ha='center')
        # init. self vars
        self.x_val = x_init
        self.x_incr = x_incr
        self.config = config
        self.axes.grid(zorder=-3)
        # post-init
        config.post_init(self.figure, self.axes)

    def process(self, data: float, passThrough: PushPipe.PassThrough) -> Image_Type:
        self.config.add_bar(data, passThrough, self)
        self.x_val += self.x_incr
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        width, height = map(int, self.figure.get_size_inches() * self.figure.get_dpi())
        return np.fromstring(self.figure.canvas.tostring_rgb(), dtype='uint8').reshape(height, width, 3)

class LinePlotRenderPipe(PushPipe[float, Image_Type]):
    @dataclass
    class LinePlotConfig():
        xlabel: str
        ylabel: str
        title: str = "Line Plot"
        aspect_ratio: float = 1
        figure_scale: float = 1
        plot_func: Callable[[List[float], List[float], PushPipe.PassThrough, plt.Figure, plt.Axes],None] = lambda x_vals, y_vals, pthru, fig, ax: ax.plot(x_vals, y_vals)

    def __init__(self, config: LinePlotConfig, x_init: float = 1, x_incr: float = 1, showWindow = False, postProcessCallback=None):
        super().__init__(postProcessCallback=postProcessCallback)
        # init. self vars
        self.x_init = x_init
        self.x_incr = x_incr
        self.yvals = []
        self.xvals = []
        self.cnt = 0
        self.config = config

    def process(self, data: float, passThrough: PushPipe.PassThrough) -> Image_Type:
        self.yvals.append(data)
        # make plot
        figure, axes = plt.subplots(figsize=(self.config.figure_scale*self.config.aspect_ratio, self.config.figure_scale))
        figure.subplots_adjust(top=0.82, bottom=0.06)
        axes.set_title(self.config.title,  position=(0.5, 1.1), ha='center')
        # plot data
        self.xvals.append(self.x_init + self.cnt*self.x_incr)
        self.config.plot_func(self.xvals, self.yvals, passThrough, figure, axes)
        self.cnt += 1
        figure.canvas.draw()
        figure.canvas.flush_events()
        width, height = map(int, figure.get_size_inches() * figure.get_dpi())
        return np.fromstring(figure.canvas.tostring_rgb(), dtype='uint8').reshape(height, width, 3)
