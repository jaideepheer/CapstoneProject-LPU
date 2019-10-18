from pipedefs.core_pipes import PushPipe
from utils.typedefs import Image_Type, AudioMetadata, AudioRecording
from cv2 import VideoCapture, cvtColor, COLOR_BGR2RGB
from pyaudio import PyAudio

class OnDemandPhotoClickPipe(PushPipe[None, Image_Type]):
    def __init__(self, postProcessCallback=None):
        super().__init__(postProcessCallback=postProcessCallback)
        self.stream = VideoCapture(0)
    def process(self, data: None, passThrough: PushPipe.PassThrough):
        status, image = self.stream.read()
        image = cvtColor(image,COLOR_BGR2RGB)
        if(status):
            return image
        else:
            self.setErrored("Stream read failed.")
            return None
    def __del__(self):
        self.stream.release()

class OnDemandAudioRecordPipe(PushPipe[None, AudioRecording]):
    def __init__(self, META: AudioMetadata, postProcessCallback=None):
        super().__init__(postProcessCallback=postProcessCallback)
        self.pyaudio = PyAudio()
        self.stream = self.pyaudio.open(format=META.Format,channels=META.Channels, rate=META.Rate, input=True, frames_per_buffer=META.Chunk_Size)
        self.METADATA = META
    def process(self, data, passThrough) -> AudioRecording:
        iters = ((self.METADATA.length*self.METADATA.Rate)//self.METADATA.Chunk_Size)+1
        data = b""
        while(iters>0):
            iters-=1
            data += self.stream.read(self.METADATA.Chunk_Size)
        return AudioRecording(METADATA=self.METADATA, data=data)
    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio.terminate()

class OnDemandEchoPipe(PushPipe[str, str]):
    def process(self, data, passThrough):
        print(data)
        return data