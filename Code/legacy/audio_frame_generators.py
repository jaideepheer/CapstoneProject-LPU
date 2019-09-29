import pyaudio

'''
Returns (RATE, format, data) with each generation where data is the audio recording of a fixed time length.
'''
def audioframe_gen_live(seconds=3, RATE=48000, CHUNK_size=1024, format=pyaudio.paFloat32, channels=1):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=format,channels=channels, rate=RATE, input=True, frames_per_buffer=CHUNK_size)
    iters = int((seconds*RATE)/CHUNK_size)
    try:
        while(True):
            data=b""
            for _ in range(iters):
                data += stream.read(CHUNK_size)
            stream.stop_stream()
            yield (RATE, data)
            stream.start_stream()
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

def playaudio(audiodata,RATE=48000, CHUNK_size=1024, format=pyaudio.paFloat32, channels=1):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=format,channels=channels, rate=RATE, output=True,frames_per_buffer=CHUNK_size)
    stream.write(audiodata)
    stream.stop_stream()
    stream.close()
    audio.terminate()