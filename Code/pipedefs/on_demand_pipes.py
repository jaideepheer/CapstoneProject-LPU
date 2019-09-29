from pipedefs.pipe import PushPipe
from utils.typedefs import Image_Type, AudioMetadata, AudioRecording
from cv2 import VideoCapture, cvtColor, COLOR_BGR2RGB
from pyaudio import PyAudio
from math import floor
import os, ffmpeg, numpy as np
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

class OnDemandVideoFrameExtractorPipe(PushPipe[None,Image_Type]):
    def __init__(self, filePath: str, ffmpeg_executable_path=os.path.abspath('./resources/ffmpeg/ffmpeg.exe'), ffprobe_executable_path="./resources/ffmpeg/ffprobe.exe", postProcessCallback=None):
        super().__init__(postProcessCallback=postProcessCallback)
        self.ffmpeg = ffmpeg_executable_path
        self.ffprobe = ffprobe_executable_path
        probe = ffmpeg.probe(filePath, cmd=self.ffprobe)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        self.width = int(video_stream['width'])
        self.height = int(video_stream['height'])
        #print(probe)
        #exit()
        self.ffmpeg_process = (
            ffmpeg
            .input(filePath)
            .output('pipe:', format='rawvideo', pix_fmt='rgb24')
            .run_async(pipe_stdout=True, cmd=self.ffmpeg)
        )
    def process(self, data: None, passThrough: PushPipe.PassThrough) -> Image_Type:
        in_bytes = self.ffmpeg_process.stdout.read(self.width * self.height * 3)
        if(not in_bytes):
            passThrough.getGlobals()['Video_EOF'] = True
            self.setErrored("Video stream ended.")
            return None
        return (np
            .frombuffer(in_bytes, np.uint8)
            .reshape([self.height, self.width, 3])
            )

class OnDemandAudioRecordPipe(PushPipe[None, AudioRecording]):
    def __init__(self, META: AudioMetadata, postProcessCallback=None):
        super().__init__(postProcessCallback=postProcessCallback)
        self.pyaudio = PyAudio()
        self.stream = self.pyaudio.open(format=META.Format,channels=META.Channels, rate=META.Rate, input=True, frames_per_buffer=META.Chunk_Size)
        self.METADATA = META
    def process(self, data, passThrough) -> AudioRecording:
        iters = floor((self.METADATA.length*self.METADATA.Rate)/self.METADATA.Chunk_Size)+1
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