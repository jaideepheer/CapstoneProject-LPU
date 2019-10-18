from pipedefs.core_pipes import PushPipe
from utils.typedefs import Image_Type
import ffmpeg, numpy as np
class OnDemandVideoFrameExtractorPipe(PushPipe[None,Image_Type]):
    def __init__(self, filePath: str, ffmpeg_executable_path='./resources/ffmpeg/ffmpeg.exe', ffprobe_executable_path="./resources/ffmpeg/ffprobe.exe", postProcessCallback=None):
        super().__init__(postProcessCallback=postProcessCallback)
        self.ffmpeg = ffmpeg_executable_path
        self.ffprobe = ffprobe_executable_path
        probe = ffmpeg.probe(filePath, cmd=self.ffprobe)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        self.width = int(video_stream['width'])
        self.height = int(video_stream['height'])
        self.total_length = int(float(probe['format']['duration']))
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
