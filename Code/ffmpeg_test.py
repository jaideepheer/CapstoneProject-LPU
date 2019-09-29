from pipedefs.on_demand_pipes import OnDemandVideoFrameExtractorPipe
from pipedefs.pipe_utils import PipeLineProfilingWrapper
import os
from sys import stdout
from cv2 import imshow, destroyAllWindows, destroyWindow, waitKey, cvtColor, COLOR_RGB2BGR
from pipedefs.pipe import PushPipe
import time, functools

def showImage_internal(winName, result, image, error, passThrough: PushPipe.PassThrough, profile: PushPipe.PipeProfile):
    if(result == PushPipe.Result.SUCCESS):
        imshow(winName, cvtColor(image,COLOR_RGB2BGR))
    else:
        #print(error)
        destroyWindow(winName)
def showImage(winName):
    return functools.partial(showImage_internal, winName)

file = os.path.abspath('./test_resources/2. A Sampling of Indian English Accents.mkv')
from face.face_detect_pipes import FaceExtractorDNNPipe
from emotion.emotion_detect_pipes import EmotionExtractorOArriagaPipe
pipeline = OnDemandVideoFrameExtractorPipe(file, postProcessCallback=showImage('video')).connect(
        FaceExtractorDNNPipe(postProcessCallback=showImage("face_DNN_callback")).connect(
            EmotionExtractorOArriagaPipe()
        )
    )

loopTime = -1
while(True):
    #print('====================================')
    loopTime = time.time() - loopTime
    #print("Loop Time: %f [%d FPS]"%(loopTime,1//loopTime))
    loopTime = time.time()
    result: PushPipe.PassThrough = pipeline.push(None, PushPipe.PassThrough())
    #print('====================================')
    if(waitKey(1) & 0xFF == ord('q') or result.getGlobals().get('Video_EOF',False)):
        break
destroyAllWindows()