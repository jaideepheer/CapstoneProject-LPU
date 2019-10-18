import gc
from keras.backend.tensorflow_backend import clear_session, get_session, set_session
from pipedefs.core_pipes import PushPipe
import tensorflow
import queue
from numba import cuda
# Reset Keras Session
def clearGPUMemory():
    sess = get_session()
    clear_session()
    sess.close()
    sess = get_session()

    # use the same config as you used to create the session
    config = tensorflow.ConfigProto()
    config.gpu_options.allow_growth = True
    config.gpu_options.per_process_gpu_memory_fraction = 1
    config.gpu_options.visible_device_list = "0"
    set_session(tensorflow.Session(config=config))
    print("Garbage collected:", gc.collect())
    cuda.select_device(0)
    cuda.close()

def clearPipeline(pipeline: PushPipe):
    q = queue.Queue()
    q.put(pipeline)
    while(not q.empty()):
        pipe = q.get()
        print("Clear pipe:",pipe)
        for c in pipe.children: q.put(c)
        del pipe