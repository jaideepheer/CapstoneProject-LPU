from pipedefs.on_demand_pipes import OnDemandPhotoClickPipe, OnDemandAudioRecordPipe
from utils.typedefs import AudioMetadata, PyAudioFormat_Type
from sys import stdout
from pipedefs.pipe_utils import PipeLineProfilingWrapper
from audio.audio_pipes import AudioPlaybackPipe, AudioToTextSphinxPipe
from pipedefs.pipe import PushPipe
from cv2 import waitKey, destroyAllWindows, imshow, destroyWindow
import functools
import time

def printStatistics(passThrough: PushPipe.PassThrough) -> float:
    print("Frame Statistics")
    print("Timings:")
    total = 0
    for X in passThrough.getExtrasHistory():
        print(X['Pipe_Type'],'-->', X['Profile.Process_Time'])
        total += X['Profile.Process_Time']
    print('Total Time:', total)
    return total

def showImage_int(winName, result, image, error, passThrough: PushPipe.PassThrough, profile: PushPipe.PipeProfile):
    if(result == PushPipe.Result.SUCCESS):
        imshow(winName, image)
    else: 
        print(error)
        destroyWindow(winName)
    #print("[%s] Average Time taken: %f sec"%(winName,profile.total_process_time/profile.process_call_count))
def showImage(winName):
    return functools.partial(showImage_int, winName)

if(False):
    from emotion.emotion_detect_pipes import EmotionExtractorOArriagaPipe
    from face.face_detect_pipes import FaceExtractorDNNPipe
    pipeline = OnDemandPhotoClickPipe(postProcessCallback=showImage("clicker_callback")).connect(
        FaceExtractorDNNPipe(postProcessCallback=showImage("face_DNN_callback")).connect(
            EmotionExtractorOArriagaPipe()
        )
    )
else:
    pipeline = OnDemandAudioRecordPipe(AudioMetadata(),postProcessCallback=None).connect(
        AudioPlaybackPipe(),
        AudioToTextSphinxPipe()
    )

pipeline = PipeLineProfilingWrapper(pipeline, stdout)
loopTime = -1
while(True):
    print('====================================')
    loopTime = time.time() - loopTime
    print("Loop Time: %f [%d FPS]"%(loopTime,1//loopTime))
    loopTime = time.time()
    result: PushPipe.PassThrough = pipeline.push(None, PushPipe.PassThrough())
    print(result.getExtrasHistory()[-1]['Process_Output'])
    print('====================================')
    if waitKey(1) & 0xFF == ord('q'):
        break
destroyAllWindows()