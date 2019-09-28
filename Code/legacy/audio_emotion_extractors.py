from keras.models import load_model
import numpy as np
import librosa
from .audio_frame_generators import *
def audioframe_emotion_gen(audioframe_gen, audio_emotion_extractor):
    try:
        for rate, audioframe in audioframe_gen:
            playaudio(audioframe)
            audioframe = np.frombuffer(audioframe, dtype=np.float32)
            yield audio_emotion_extractor.getAudioEmotionDistribution(audioframe, rate)
    finally:
        audioframe_gen.close()

class audioframe_emotion_extractor:
    def __init__(self, kerasModelPath="./resources/audio_sentiment/marcogdepinto/Emotion_Voice_Detection_Model_Manual.h5"):
        self.model = load_model(kerasModelPath)
        print(self.model.summary())
    
    def getAudioEmotionDistribution(self, audioframedata, sample_rate):
        # pre-processing
        MFCC = np.mean(librosa.feature.mfcc(y=audioframedata, sr=sample_rate, n_mfcc=40).T, axis=0)
        print(MFCC.shape)
        MFCC = np.expand_dims(MFCC, axis = 2)
        MFCC = np.expand_dims(MFCC, axis = 0)
        print("MFCC", MFCC.shape)
        print(MFCC)
        return self.model.predict_classes(MFCC)
