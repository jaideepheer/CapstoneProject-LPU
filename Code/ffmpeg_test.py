from video.video_pipes import OnDemandVideoFrameExtractorPipe
from pipedefs.pipe_utils import PipeLineProfilingWrapper
import os
from emotion.face_emotion_detect_pipes import Emotions_Type
from sys import stdout
from cv2 import imshow, destroyAllWindows, destroyWindow, waitKey, cvtColor, COLOR_RGB2BGR
from pipedefs.core_pipes import PushPipe
import time, functools

def showImage_internal(winName, result, image, error, passThrough: PushPipe.PassThrough, profile: PushPipe.PipeProfile):
    if(result == PushPipe.Result.SUCCESS):
        imshow(winName, cvtColor(image,COLOR_RGB2BGR))
    else:
        #print(error)
        destroyWindow(winName)
def showImage(winName):
    return functools.partial(showImage_internal, winName)

file = os.path.abspath('./test_resources/1. IELTS Speaking Exam - How to Do Part One of the IELTS Speaking Exam.mkv')
from face.face_detect_pipes import FaceExtractorDNNPipe
from emotion.face_emotion_detect_pipes import EmotionExtractorOArriagaPipe
from gui.gui_pipes import RadarChartRenderPipe
from pipedefs.core_pipes import ProcessPushPipe
from utils.typedefs import Image_Type
from typing import List
pipeline = OnDemandVideoFrameExtractorPipe(file, postProcessCallback=showImage('video')).connect(
        FaceExtractorDNNPipe(postProcessCallback=showImage("face_DNN_callback")).connect(
            EmotionExtractorOArriagaPipe().connect(
                ProcessPushPipe[Emotions_Type, List[float]](
                    lambda self, emo, passthrough: list(emo._asdict().values())
                ).connect(
                    RadarChartRenderPipe(RadarChartRenderPipe.RadarChartConfig(
                        labels=Emotions_Type._fields,
                        frame='polygon',
                        figure_size=(4,3)
                    ), showWindow=False)
                )
            )
        )
    )

pipeline = PipeLineProfilingWrapper(pipeline, stdout)
loopTime = -1
while(True):
    print('====================================')
    loopTime = time.time() - loopTime
    print("Loop Time: %f [%d FPS]"%(loopTime,1//loopTime))
    loopTime = time.time()
    result: PushPipe.PassThrough = pipeline.push(None, PushPipe.PassThrough())
    output = result.getExtrasHistory()
    if len(output) > 2:
        output = output[2]['Process_Output']
        if isinstance(output, Emotions_Type):
            output = output._asdict()
            print(max(output, key=output.get))
        output = result.getCurrentExtras()['Process_Output']
        if isinstance(output, Image_Type):
            imshow('emotion_chart',output)
    print('====================================')
    if(waitKey(1) & 0xFF == ord('q') or result.getGlobals().get('Video_EOF',False)):
        break
destroyAllWindows()