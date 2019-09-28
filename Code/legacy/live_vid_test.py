from cv2 import VideoCapture, circle, imshow, waitKey, destroyAllWindows, destroyWindow
from .face_feature_extractors import face_feature_extractor_dlib68
from .face_detectors import face_detector_dlib
from .emotion_extractors import emotion_extractor_oarriaga
from ..utils.typedefs import *

def getCroppedImage(image, rectangle):
    return image[rectangle[1]:rectangle[3], rectangle[0]:rectangle[2]]

face_detector = face_detector_dlib()
face_feature = face_feature_extractor_dlib68()
emotion_extractor = emotion_extractor_oarriaga()
stream = VideoCapture(0)
while(True):
    img = stream.read()[1]
    faceRect = face_detector.getFaceBoundingBox(img)
    if(faceRect == (0,0,0,0)):
        print("no face")
        destroyWindow('face')
    else:
        faceImg = getCroppedImage(img, faceRect)
        features = face_feature.getFaceFeaturePoints(img, faceRect)
        print(faceRect)
        emotions = emotion_extractor.getFaceEmotionDistribution(faceImg)
        print(emotions)
        for (x, y) in features:
	        circle(img, (x, y), 1, (0, 0, 255), -1)
        imshow('face', faceImg)
    imshow('img',img)
    if waitKey(1) & 0xFF == ord('q'):
        break
stream.release()
destroyAllWindows()