from abc import ABC, abstractmethod
from utils.typedefs import BoundingBox_twopoint
from utils.image_utils import dlibrect_to_BoundingBox_twopoint

import cv2
import numpy as np
import dlib

class face_detector(ABC):
    @abstractmethod
    def getFaceBoundingBox(self, image: np.ndarray) -> BoundingBox_twopoint:
        pass

class face_detector_cascade(face_detector):
    def __init__(self, cascadeXMLFilePath='./resources/face_detectors/facedetect_haarcascade_frontalface_default.xml'):
        if(not(type(cascadeXMLFilePath) is str)):
            raise TypeError("face_extractor constructor was sent invalid argument. 'cv2Mode' must be string.")
        # check if file exists
        open(cascadeXMLFilePath,'r').close()
        self.face_cascade = cv2.CascadeClassifier(cascadeXMLFilePath)
    
    def getFaceBoundingBox(self, imageArray: np.ndarray) -> BoundingBox_twopoint:
        # Returns the (left, top, right, bottom) positions of
        #   the bounding box around the largest area face found.
        # If no face is found, it returns the (0,0,0,0) box positions.
        gray = cv2.cvtColor(imageArray, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        # get largest face
        largest = (0,0,0,0)
        for (x,y,w,h) in faces:
            if(largest[-1]*largest[-2]<w*h):
                largest = (x,y,w,h)
        # return largest face's bounding box co-ordinates
        (x,y,w,h) = largest
        return BoundingBox_twopoint(x,y,x+w,y+h)

class face_detector_dnn(face_detector):
    def __init__(self, dnnModelFile="./resources/face_detectors/facedetect_dnn_res10_300x300_ssd_iter_140000_fp16.caffemodel", dnnConfigFile="./resources/face_detectors/facedetect_dnn_deploy.prototxt", confidenceThreshold = .6, ignoreOutOfBoundDetections=True):
        # check files
        open(dnnConfigFile,'r').close()
        open(dnnModelFile,'r').close()
        self.net = cv2.dnn.readNetFromCaffe(dnnConfigFile, dnnModelFile)
        self.confidenceThreshold = confidenceThreshold
        self.ignoreOutOfBoundDetections = ignoreOutOfBoundDetections
    
    def getFaceBoundingBox(self, imageArray: np.ndarray) -> BoundingBox_twopoint:
        # Returns the (left, top, right, bottom) positions of
        #   the bounding box around the largest area face found.
        # If no face is found, it returns the (0,0,0,0) box positions.
        height, width, channels = imageArray.shape[0:3]
        assert channels == 3
        blob = cv2.dnn.blobFromImage(cv2.resize(imageArray, (300,300)), 1.0, (300, 300), [104, 117, 123], False, False)
        self.net.setInput(blob)
        detections = self.net.forward()
        # get largest face
        largest = [0,0,0,0]
        prevArea = 0
        for i in range(0, detections.shape[2]):
            if(detections[0, 0, i, 2]<self.confidenceThreshold):
                continue
            (startX, startY, endX, endY) = detections[0, 0, i, 3:7]
            area = (startX-endX)*(startY-endY)
            if(prevArea<area):
                prevArea = area
                largest = [startX, startY, endX, endY]
        largest = np.asarray(largest)
        for i in largest:
            if(i>1):
                if self.ignoreOutOfBoundDetections:
                    return BoundingBox_twopoint(0,0,0,0)
                else:
                    # try to normalise detections
                    largest *= 1.0/max(largest)
                    largest = largest.tolist()
                    break
        return BoundingBox_twopoint(int(largest[0] * width), int(largest[1] * height), int(largest[2] * width), int(largest[3] * height))

class face_detector_dlib(face_detector):
    def __init__(self):
        self.model = dlib.get_frontal_face_detector()
    
    def getFaceBoundingBox(self, image: np.ndarray, upscaling_layers: int=1) -> BoundingBox_twopoint:
        # Returns the (top, left, bottom, right) positions of
        #   the bounding box around the largest area face found.
        # If no face is found, it returns the (0,0,0,0) box positions.
        rects = self.model(image, upscaling_layers)
        if(len(rects)>0):
            return dlibrect_to_BoundingBox_twopoint(rects[0])
        else:
            return BoundingBox_twopoint(0,0,0,0)