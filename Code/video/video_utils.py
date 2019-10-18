from utils.typedefs import Image_Type
from os import system
import ffmpeg, numpy as np
def getVideoThumbnail(videoFilePath, position=0.05, ffmpeg_executable_path='./resources/ffmpeg/ffmpeg.exe', ffprobe_executable_path="./resources/ffmpeg/ffprobe.exe") -> Image_Type:
    # get video info
    probe = ffmpeg.probe(videoFilePath, cmd=ffprobe_executable_path)
    total_length = int(float(probe['format']['duration']))
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    width = int(video_stream['width'])
    height = int(video_stream['height'])
    # extract thumbnail
    image,_ = (
        ffmpeg
        .input(videoFilePath, ss=total_length*position)
        .output('pipe:', vframes=1, format='rawvideo', pix_fmt='rgb24')
        .run(capture_stdout=True, cmd=ffmpeg_executable_path)
    )
    return np.frombuffer(image, np.uint8).reshape([height, width, 3])

def saveVideoThumbnail(videoFilePath, saveImagePath, position=0.05, ffmpeg_executable_path='./resources/ffmpeg/ffmpeg.exe', ffprobe_executable_path="./resources/ffmpeg/ffprobe.exe"):
    # get video info
    probe = ffmpeg.probe(videoFilePath, cmd=ffprobe_executable_path)
    total_length = int(float(probe['format']['duration']))
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    width = int(video_stream['width'])
    height = int(video_stream['height'])
    # extract thumbnail
    (
        ffmpeg
        .input(videoFilePath, ss=total_length*position)
        .output(saveImagePath, vframes=1, format='image2', vcodec='mjpeg')
        .run(cmd=ffmpeg_executable_path)
    )