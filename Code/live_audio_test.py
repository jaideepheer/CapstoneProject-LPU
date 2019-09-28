from audio.audio_frame_generators import audioframe_gen_live
from audio.audio_emotion_extractors import *
# test
emo_map=["neutral","calm","happy","sad","angry", "fearful", "disgust", "surprised"]
print("begin test")

for emotion in audioframe_emotion_gen(audioframe_gen_live(), audioframe_emotion_extractor()):
    print("Done.")
    print("emotion=",emo_map[emotion[0]])
    print("Recording")