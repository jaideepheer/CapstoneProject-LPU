from pyaudio import PyAudio
from pipedefs.pipe import PushPipe
from utils.typedefs import AudioRecording
from speech_recognition import AudioData, Recognizer, UnknownValueError
import numpy as np
from dataclasses import dataclass
import deepspeech

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

class AudioToTextDeepSpeechPipe(PushPipe[AudioRecording, str]):
    @dataclass
    class LanguageModel_Config:
        lm_path: str
        trie_path: str
        # The alpha hyperparameter of the CTC decoder. Language Model weight
        LM_WEIGHT: float = 1.5
        # The beta hyperparameter of the CTC decoder. Word insertion bonus.
        VALID_WORD_COUNT_WEIGHT: float = 2.25
    def __init__(self, model_pb_path: str, alphabet_path: str, beam_width: int = 512, language_model: LanguageModel_Config = None,  postProcessCallback=None):
        super().__init__(postProcessCallback=postProcessCallback)
        self.model = deepspeech.Model(model_pb_path, alphabet_path, beam_width)
        if(language_model is not None):
            self.model.enableDecoderWithLM(language_model.lm_path, language_model.trie_path, language_model.LM_WEIGHT, language_model.VALID_WORD_COUNT_WEIGHT)
        self.stream_state = None
        self.beam_width = beam_width
    def process(self, recording: AudioRecording, passThrough: PushPipe.PassThrough):
        self.stream_state = self.model.createStream(recording.METADATA.Rate)
        data = np.frombuffer(recording.data, np.int16)
        padding = (self.beam_width - (data.shape[0]%self.beam_width))%self.beam_width
        data = np.pad(data, (0, padding), 'constant')
        print("Total:",data.shape)
        data = np.split(data, self.beam_width)
        print('Data:',len(data),data[0].shape,data[-1].shape)
        # feed samples to stream
        for frame in data:
            self.model.feedAudioContent(self.stream_state, frame)
        return self.model.finishStream(self.stream_state)

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