from pipedefs.on_demand_pipes import OnDemandPhotoClickPipe, OnDemandAudioRecordPipe, OnDemandAudioFrameExtractor
from utils.typedefs import AudioMetadata, PyAudioFormat_Type
from sys import stdout
from pipedefs.pipe_utils import PipeLineProfilingWrapper
from audio.audio_pipes import AudioPlaybackPipe, AudioToTextSphinxPipe, AudioToTextDeepSpeechPipe
from pipedefs.pipe import PushPipe, ProcessPushPipe
from cv2 import waitKey, destroyAllWindows, imshow, destroyWindow, cvtColor, COLOR_RGB2BGR
import functools
import time

def showImage_internal(winName, result, image, error, passThrough: PushPipe.PassThrough, profile: PushPipe.PipeProfile):
    if(result == PushPipe.Result.SUCCESS):
        imshow(winName, cvtColor(image,COLOR_RGB2BGR))
    else: 
        print(error)
        destroyWindow(winName)
def showImage(winName):
    return functools.partial(showImage_internal, winName)

if(False):
    from emotion.emotion_detect_pipes import EmotionExtractorOArriagaPipe
    from face.face_detect_pipes import FaceExtractorMTCNNPipe, FaceExtractorDNNPipe
    pipeline = OnDemandPhotoClickPipe(postProcessCallback=showImage("clicker_callback")).connect(
        FaceExtractorDNNPipe(postProcessCallback=showImage("face_DNN_callback")).connect(
            EmotionExtractorOArriagaPipe()
        )
    )
else:
    import os
    from gui.gui_pipes import BarChartSequentialRenderPipe
    from emotion.text_sentiment_detect_pipes import SentimentExtractorVaderPipe
    file = os.path.abspath('./test_resources/1. IELTS Speaking Exam - How to Do Part One of the IELTS Speaking Exam.mkv')
    pipeline = OnDemandAudioFrameExtractor(file,AudioMetadata(),postProcessCallback=None).connect(
        AudioPlaybackPipe(),
        AudioToTextDeepSpeechPipe("C:/Users/hp/Desktop/deepspeech/mozDS/deepspeech-0.5.1-models/deepspeech-0.5.1-models/output_graph.pb","C:/Users/hp/Desktop/deepspeech/mozDS/deepspeech-0.5.1-models/deepspeech-0.5.1-models/alphabet.txt", language_model=AudioToTextDeepSpeechPipe.LanguageModel_Config("C:/Users/hp/Desktop/deepspeech/mozDS/deepspeech-0.5.1-models/deepspeech-0.5.1-models/lm.binary","C:/Users/hp/Desktop/deepspeech/mozDS/deepspeech-0.5.1-models/deepspeech-0.5.1-models/trie")).connect(
            ProcessPushPipe[str, float](
                lambda self, s, passthru: len(s.split())
            ).connect(
                BarChartSequentialRenderPipe(BarChartSequentialRenderPipe.BarChartConfig("words", "Time"),3,3,postProcessCallback=showImage('bar_chart'))
            ),
            SentimentExtractorVaderPipe()
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
    print("Text:",result.getExtrasHistory()[-4]['Process_Output'])
    print("Sentiment:",result.getExtrasHistory()[-1]['Process_Output'])
    print('====================================')
    if waitKey(1) & 0xFF == ord('q'):
        break
destroyAllWindows()