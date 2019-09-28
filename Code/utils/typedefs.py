from typing import NamedTuple, ByteString
from enum import IntEnum
from dataclasses import dataclass
import numpy as np
from pyaudio import paFloat32, paInt32, paInt16, paInt24, paInt8, paUInt8, paCustomFormat

# PyAudio Audio Format
class PyAudioFormat_Type(IntEnum):
    T_paFloat32 = paFloat32
    T_paInt16 = paInt16
    T_paInt24 = paInt24
    T_paInt32 = paInt32
    T_paInt8 = paInt8
    T_paUInt8 = paUInt8
    T_paCustomFormat = paCustomFormat
# Audio Types
@dataclass
class AudioMetadata:
    length: int = 3
    Rate: int = 16000
    Chunk_Size: int = 2048
    Channels: int = 1
    Format: PyAudioFormat_Type = paInt16
    def getFormatByteSize(self):
        if(self.Format == PyAudioFormat_Type.T_paFloat32 or
            self.Format == PyAudioFormat_Type.T_paInt32): return 4
        elif(self.Format == PyAudioFormat_Type.T_paInt8 or
            self.Format == PyAudioFormat_Type.T_paUInt8): return 1
        elif(self.Format == PyAudioFormat_Type.T_paInt16): return 2
        elif(self.Format == PyAudioFormat_Type.T_paInt24): return 3
        return 0
@dataclass
class AudioRecording:
    METADATA: AudioMetadata
    data: ByteString

# (left, top, width, height)
BoundingBox_onepoint = NamedTuple('BoundingBox_onepoint',[('left',int), ('top',int), ('width',int), ('height',int)])
# (left, top, right, bottom)
BoundingBox_twopoint = NamedTuple('BoundingBox_twopoint',[('left',int), ('top',int), ('right',int), ('bottom',int)])

# image
Image_Type = np.ndarray

# emotion
Emotions_Type = NamedTuple('Emotions', [
    ('angry', float),
    ('disgust', float),
    ('fear',  float),
    ('happy',  float),
    ('sad',  float),
    ('surprise',  float),
    ('neutral', float)
])