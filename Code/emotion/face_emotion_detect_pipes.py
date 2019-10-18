from pipedefs.core_pipes import PushPipe
from utils.typedefs import Image_Type, Emotions_Type
from cv2 import COLOR_BGR2GRAY, cvtColor, resize
from keras.preprocessing import image
from keras.models import model_from_json, load_model
import numpy as np
class EmotionExtractorSarengilPipe(PushPipe[Image_Type, Emotions_Type]):
    def __init__(self, kerasModelPath="./resources/sarengil/facial_expression_model_structure.json", kerasModelWeightsPath="./resources/sarengil/facial_expression_model_weights.h5", postProcessCallback=None):
        super().__init__(postProcessCallback=postProcessCallback)
        self.model = model_from_json(open(kerasModelPath, "r").read())
        self.model.load_weights(kerasModelWeightsPath)
    def process(self, data, passThrough):
        # pre-processing
        data = cvtColor(data, COLOR_BGR2GRAY)
        data = resize(data, self.model.input_shape[1:3])
        img_pixels = image.img_to_array(data)
        img_pixels = np.expand_dims(img_pixels, axis = 0)
        img_pixels /= 255 # normalize to be within [0,1]
        # get nn predictions
        predictions = Emotions_Type(*self.model.predict(img_pixels).tolist()[0])
        return predictions
    def __del__(self):
        del self.model

# Better Pipe
class EmotionExtractorOArriagaPipe(PushPipe[Image_Type, Emotions_Type]):
    def __init__(self, kerasModelPath="./resources/oarriaaga/fer2013_mini_XCEPTION.107-0.66.hdf5", postProcessCallback=None):
        super().__init__(postProcessCallback=postProcessCallback)
        self.model = load_model(kerasModelPath, compile=False)
    def preprocess_input(self, x, v2=True):
        x = x.astype('float32')
        x = x / 255.0
        if v2:
            x = x - 0.5
            x = x * 2.0
        return x
    def process(self, data, passThrough):
        # pre-processing
        data = cvtColor(data, COLOR_BGR2GRAY)
        data = resize(data, (self.model.input_shape[1:3]))
        img_pixels = self.preprocess_input(data, True)
        img_pixels = np.expand_dims(img_pixels, axis = 0)
        img_pixels = np.expand_dims(img_pixels, axis = -1)
        # get nn predictions
        predictions = Emotions_Type(*self.model.predict(img_pixels).tolist()[0])
        return predictions
    def __del__(self):
        del self.model