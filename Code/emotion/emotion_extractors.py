import numpy as np
import cv2
from keras.preprocessing import image
from keras.models import model_from_json
from keras.models import load_model

class emotion_extractor_sarengil:
    def __init__(self, kerasModelPath="./resources/sarengil/facial_expression_model_structure.json", kerasModelWeightsPath="./resources/sarengil/facial_expression_model_weights.h5"):
        self.model = model_from_json(open(kerasModelPath, "r").read())
        self.model.load_weights(kerasModelWeightsPath)
        self.emotions = ('angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral')
    
    def getEmotionsTupple(self):
        return self.emotions
    
    def getFaceEmotionDistribution(self, imageData):
        # pre-processing
        imageData = cv2.cvtColor(imageData, cv2.COLOR_BGR2GRAY)
        imageData = cv2.resize(imageData, self.model.input_shape[1:3])
        img_pixels = image.img_to_array(imageData)
        img_pixels = np.expand_dims(img_pixels, axis = 0)
        img_pixels /= 255 # normalize to be within [0,1]
        # get nn predictions
        predictions = (self.model.predict(img_pixels)*100).tolist()[0] # scale predictions to be within [0,100]
        predictions = dict(zip(self.emotions, predictions))
        return predictions


class emotion_extractor_oarriaga:
    def __init__(self, kerasModelPath="./resources/oarriaaga/fer2013_mini_XCEPTION.107-0.66.hdf5"):
        self.model = load_model(kerasModelPath, compile=False)
        self.emotions = ('angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral')
    
    def getEmotionsTupple(self):
        return self.emotions
    
    def getFaceEmotionDistribution(self, imageData):
        # pre-processing
        imageData = cv2.cvtColor(imageData, cv2.COLOR_BGR2GRAY)
        imageData = cv2.resize(imageData, (self.model.input_shape[1:3]))
        img_pixels = self.preprocess_input(imageData, True)
        img_pixels = np.expand_dims(img_pixels, axis = 0)
        img_pixels = np.expand_dims(img_pixels, axis = -1)
        # get nn predictions
        predictions = (self.model.predict(img_pixels)*100).tolist()[0] # scale predictions to be within [0,100]
        predictions = dict(zip(self.emotions, predictions))
        return predictions
    
    def preprocess_input(self, x, v2=True):
        x = x.astype('float32')
        x = x / 255.0
        if v2:
            x = x - 0.5
            x = x * 2.0
        return x
