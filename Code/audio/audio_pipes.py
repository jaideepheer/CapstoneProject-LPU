from pyaudio import PyAudio
from pipedefs.pipe import PushPipe
from utils.typedefs import AudioRecording

class AudioPlaybackPipe(PushPipe[AudioRecording, AudioRecording]):
    def __init__(self, postProcessCallback=None):
        super().__init__(postProcessCallback=postProcessCallback)
        self.pyaudio = PyAudio()
        self.stream = None
    def process(self, recording: AudioRecording, passThrough: PushPipe.PassThrough) -> AudioRecording:
        if(self.stream is None):
            META = recording.METADATA
            self.stream = self.pyaudio.open(format=META.Format,channels=META.Channels, rate=META.Rate, output=True, frames_per_buffer=META.Chunk_Size)
        self.stream.write(recording.data)
        return recording
    def __del__(self):
        if(self.stream is not None):
            self.stream.stop_stream()
            self.stream.close()
        self.pyaudio.terminate()

from speech_recognition import AudioData, Recognizer, UnknownValueError
class AudioToTextSphinxPipe(PushPipe[AudioRecording,str]):
    def __init__(self, postProcessCallback=None):
        super().__init__(postProcessCallback=postProcessCallback)
        self.sr = Recognizer()
    def process(self, recording: AudioRecording, passThrough: PushPipe.PassThrough):
        print('Sample width:',recording.METADATA.getFormatByteSize())
        data = AudioData(recording.data, recording.METADATA.Rate, recording.METADATA.getFormatByteSize())
        try:
            return self.sr.recognize_sphinx(data,'en-IN')
        except UnknownValueError:
            self.setErrored("Couldn't identify speech.")
            return ''