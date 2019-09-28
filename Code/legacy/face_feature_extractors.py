import dlib
import numpy as np
from .image_utils import BoundingBox_twopoint_to_dlibrect

class face_feature_extractor_dlib68:
    def __init__(self, dlib68_faceshape_predictor_path="./resources/face_feature_extractors/dlib_68_point/shape_predictor_68_face_landmarks.dat"):
        self.model = dlib.shape_predictor(dlib68_faceshape_predictor_path)
        self.tempfacedetect = dlib.get_frontal_face_detector()

    def getFaceFeaturePoints(self, imageData, faceRect):
        faceRect = BoundingBox_twopoint_to_dlibrect(faceRect)
        return self.shape_to_np(self.model(imageData,faceRect))
    
    def shape_to_np(self, shape, dtype=int):
        # initialize the list of (x, y)-coordinates
        coords = np.zeros((68, 2), dtype=dtype)
        # loop over the 68 facial landmarks and convert them
        # to a 2-tuple of (x, y)-coordinates
        for i in range(0, 68):
            coords[i] = (shape.part(i).x, shape.part(i).y) 
        # return the list of (x, y)-coordinates
        return coords