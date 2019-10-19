from video.video_pipes import OnDemandVideoFrameExtractorPipe
from audio.audio_pipes import OnDemandAudioFrameExtractor, AudioToTextDeepSpeechPipe
from face.face_detect_pipes import FaceExtractorDNNPipe
from emotion.face_emotion_detect_pipes import EmotionExtractorOArriagaPipe
from emotion.text_sentiment_detect_pipes import SentimentExtractorVaderPipe
from pipedefs.core_pipes import ProcessPushPipe, PushPipe
from pipedefs.pipe_utils import PipeLineProfilingWrapper
from gui.gui_pipes import RadarChartRenderPipe, BarChartSequentialRenderPipe, LinePlotRenderPipe
from utils.typedefs import Emotions_Type, AudioMetadata, Emotions_Type, _GOLDEN_RATIO_FLOAT_, TextSentimentVader
from utils.memory_util import clearGPUMemory, clearPipeline
import threading
from gui.tkinter.processing_windows import ProcessingWindow
from sys import stdout
from abc import ABCMeta, abstractmethod
from typing import List, Union
from operator import add as add_operator

class ThreadedFileWorker(threading.Thread, metaclass=ABCMeta):
    def __init__(self, filePath, processingGUIWindow: ProcessingWindow):
        threading.Thread.__init__(self)
        # setup state vars
        self.abort = False
        self.pause = False
        self.result = dict()
        # bind with gui
        gui = processingGUIWindow
        gui.abortCallback = self.setAbort
        gui.pauseCallback = self.setPause
        gui.resumeCallback = self.resetPause
        self.gui = gui
        self.filepath = filePath
        self.waiter = threading.Event()
        self.waiter.clear()

    def getFinalResult(self) -> dict: return self.result
    
    def setAbort(self):
        self.abort = True
        self.resetPause()

    def setPause(self):
        self.waiter.clear()
        self.pause = True

    def resetPause(self):
        self.pause = False
        self.waiter.set()
    
    def run(self):
        print("Creating Pipeline...")
        pipeline = self.setupPipeline()
        print("Pipeline created. Run processing...")
        while(True):
            if self.pause:
                print("Worker paused.")
                self.waiter.wait()
                print("Worker resumed.")
            if self.abort:
                # got abort signal
                break
            try:
                processingDone = self.processPipelineTick(pipeline)
            except Exception as e:
                print("Worker thread caught exception. Will stop processing now.")
                print(e)
                break
            if processingDone:
                # processing done, close gui manually
                self.gui.onProcessingComplete()
                break
        # post-processing
        try:
            self.doPostProcessing()
        except Exception as e:
            print("Worker thread exception during post-processing.")
            print(e)
        # clear memory
        if isinstance(pipeline, PipeLineProfilingWrapper):
            pipeline = pipeline.pipeline
        clearPipeline(pipeline)
        clearGPUMemory()

    @abstractmethod
    def processPipelineTick(self, pipeline) -> bool:
        pass
    @abstractmethod
    def setupPipeline(self) -> Union[PushPipe, PipeLineProfilingWrapper]:
        pass
    @abstractmethod
    def doPostProcessing(self):
        pass

class VideoWorker(ThreadedFileWorker):
    def __init__(self, filePath, processingGUIWindow, printProfiling=True, profilingStream=stdout):
        super().__init__(filePath, processingGUIWindow)
        self.printProfiling = printProfiling
        self.profilingStream = profilingStream
        self.total_emotion = Emotions_Type(0,0,0,0,0,0,0)
        self.emoFrames = 0
        self.dominant_emotion_max = 0
        self.result['Total_Frames_Processed'] = 0
        self.result['FramesWithFace'] = 0
    
    def doPostProcessing(self):
        avgEmo = [a/self.emoFrames for a in self.total_emotion]
        image = self.radarPipe.push(avgEmo, PushPipe.PassThrough()).getCurrentExtras()['Process_Output']
        self.result['OverallEmotionChart'] = image

    def processPipelineTick(self, pipeline):
        result: PushPipe.PassThrough = pipeline.push(None, PushPipe.PassThrough())
        if result.getGlobals().get('Video_EOF',False):
            # reached EOF processing processing done
            return True
        output = result.getExtrasHistory()
        depth = len(output)
        vidFrame = output[0]['Process_Output']
        self.result['Total_Frames_Processed'] += 1
        faceFrame = None
        emoFrame = None
        if depth > 1 and output[1]['Process_Result'] == PushPipe.Result.SUCCESS:
            faceFrame = output[1]['Process_Output']
            self.result['FramesWithFace'] += 1
        if depth > 2 and output[2]['Process_Result'] == PushPipe.Result.SUCCESS:
            emotions = output[2]['Process_Output']
            self.total_emotion = Emotions_Type(*map(add_operator, self.total_emotion, emotions))
            self.emoFrames += 1
            # calc. dominant emotion frame
            emotions = emotions._asdict()
            maxEmo, emoName = max(zip(emotions.values(), emotions.keys()))
            if maxEmo >= self.dominant_emotion_max:
                self.dominant_emotion_max = maxEmo
                self.result['DominantEmotion'] = emoName
                self.result['DominantEmotionFrame'] = vidFrame
                self.result['DominantEmotionFaceFrame'] = faceFrame
        if depth > 4 and output[4]['Process_Result'] == PushPipe.Result.SUCCESS:
            emoFrame = output[4]['Process_Output']
        # send data to gui
        self.gui.refreshProcessingData(faceFrame,vidFrame,emoFrame)
        return False
    
    def setupPipeline(self):
        radarPipe = RadarChartRenderPipe(
                                RadarChartRenderPipe.RadarChartConfig(
                                    labels=Emotions_Type._fields,
                                    frame='polygon',
                                    figure_size=(4,3)
                                )
                            )
        self.radarPipe = radarPipe
        pipeline = (
            OnDemandVideoFrameExtractorPipe(self.filepath)
            .connect(
                FaceExtractorDNNPipe()
                .connect(
                    EmotionExtractorOArriagaPipe()
                    .connect(
                        ProcessPushPipe[Emotions_Type, List[float]](
                            lambda self, emo, passthrough: list(emo._asdict().values())
                        )
                        .connect(
                            radarPipe
                            )
                        )
                    )
                )
            )
        if self.printProfiling:
            pipeline = PipeLineProfilingWrapper(pipeline, self.profilingStream)
        return pipeline

class AudioWorker(ThreadedFileWorker):
    def __init__(self, filePath, processingGUIWindow, printProfiling=True, profilingStream=stdout):
        super().__init__(filePath, processingGUIWindow)
        self.printProfiling = printProfiling
        self.profilingStream = profilingStream
        self.audioMetaConfig = AudioMetadata()
        self.result['Total_WordCount'] = 0
        self.result['TotalTimeProcessed'] = 0
    
    def doPostProcessing(self):
        self.result['WordsPerSecond'] = self.result['Total_WordCount']/self.result['TotalTimeProcessed']
    
    def processPipelineTick(self, pipeline):
        result: PushPipe.PassThrough = pipeline.push(None, PushPipe.PassThrough())
        if result.getGlobals().get('Audio_EOF',False):
            # reached EOF processing processing done
            return True
        output = result.getExtrasHistory()
        depth = len(output)
        audioFrame = output[0]['Process_Output']
        text = None
        barChart = None
        emoGraph = None
        if depth > 1 and output[1]['Process_Result'] == PushPipe.Result.SUCCESS:
            text = output[1]['Process_Output']
            self.result['TotalTimeProcessed'] += self.audioMetaConfig.length
        if depth > 3 and output[3]['Process_Result'] == PushPipe.Result.SUCCESS:
            barChart = output[3]['Process_Output']
            self.result['WordCountChart'] = barChart
            self.result['Total_WordCount'] += output[2]['Process_Output']
        if depth > 6 and output[6]['Process_Result'] == PushPipe.Result.SUCCESS:
            print(output[4]['Process_Output'])
            emoGraph = output[6]['Process_Output']
            self.result['SentimentChart'] = emoGraph
        # send data to gui
        self.gui.refreshProcessingData(barChart,emoGraph)
        return False
    
    @staticmethod
    def lineplot(x_vals, y_vals, pthru, fig, ax):
        ax.set_ylim(-1,1)
        ax.fill_between(x_vals, y_vals, facecolor='lightsalmon', edgecolor='orangered', linewidth=3)
    
    @staticmethod
    def barplot(yval, pthru, slf):
        c='grey'
        if yval>0: c = 'g'
        elif yval<0: c = 'r'
        slf.axes.bar(slf.x_val, yval, color=c, zorder=3)
    
    def setupPipeline(self):
        frameTimeSec = self.audioMetaConfig.length
        pipeline = (
            OnDemandAudioFrameExtractor(self.filepath, self.audioMetaConfig)
            .connect(
                AudioToTextDeepSpeechPipe()
                .connect(
                    ProcessPushPipe[str, float](
                        lambda self, s, passthru: len(s.split())
                    ).connect(
                        BarChartSequentialRenderPipe(
                            BarChartSequentialRenderPipe.BarChartConfig("Word Count", "Time(sec.)","Word Frequency", _GOLDEN_RATIO_FLOAT_, 5,
                            add_bar=lambda data, psthru, slf: (
                                    slf.axes.bar(slf.x_val, data, color='b', zorder=3)
                                )
                            ), frameTimeSec,frameTimeSec
                        )
                    ),
                    SentimentExtractorVaderPipe()
                    .connect(
                        ProcessPushPipe[TextSentimentVader, float](
                            lambda self, data, passthru: data.compound
                        )
                        .connect(
                            BarChartSequentialRenderPipe(
                                BarChartSequentialRenderPipe.BarChartConfig(
                                    "Compound Sentiment", "Time(Sec.)", "Text Sentiment", _GOLDEN_RATIO_FLOAT_, 5,
                                    post_init=lambda fig, axes: (
                                        axes.set_ylim(-1,1)
                                    ),
                                    add_bar=AudioWorker.barplot
                                ), frameTimeSec, frameTimeSec
                            )
                            # LinePlotRenderPipe(LinePlotRenderPipe.LinePlotConfig(
                            #     "Compound Sentiment", "Time(Sec.)", "Text Sentiment", _GOLDEN_RATIO_FLOAT_, 5, plot_func=AudioWorker.lineplot
                            # ), frameTimeSec, frameTimeSec)
                        )
                    )
                )
            )
        )
        if self.printProfiling:
            pipeline = PipeLineProfilingWrapper(pipeline, self.profilingStream)
        return pipeline
