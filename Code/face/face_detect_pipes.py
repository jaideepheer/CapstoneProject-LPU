from pipedefs.pipe import PushPipe
from utils.typedefs import Image_Type
from cv2 import CascadeClassifier, cvtColor, COLOR_BGR2GRAY, dnn, resize
from utils.typedefs import BoundingBox_twopoint
from utils.image_utils import dlibrect_to_BoundingBox_twopoint
from abc import abstractmethod
import dlib
class FaceExtractorPipe(PushPipe[Image_Type, Image_Type]):
    def process(self, image, passThrough):
        rect = self.getFaceBB(image, passThrough)
        if(self.result == PushPipe.Result.SUCCESS):
            passThrough.getCurrentExtras()['Face.Bounding_Box'] = rect
            return image[rect.top:rect.bottom, rect.left:rect.right]
        else:
            passThrough.getCurrentExtras()['Face.Bounding_Box'] = None
            return image
    @abstractmethod
    def getFaceBB(self, image: Image_Type, passThrough: PushPipe.PassThrough) -> BoundingBox_twopoint:
        pass
class FaceExtractorDLibPipe(FaceExtractorPipe):
    def __init__(self, upscaling_layers: int=1, postProcessCallback=None):
        super().__init__(postProcessCallback=postProcessCallback)
        self.model = dlib.get_frontal_face_detector()
        self.upscaling_layers = upscaling_layers
    def getFaceBB(self, image: Image_Type, passThrough: PushPipe.PassThrough) -> Image_Type:
        rects = self.model(image, self.upscaling_layers)
        if(len(rects)>0):
            rect = rects[0]
            return dlibrect_to_BoundingBox_twopoint(rect)
        else:
            # no faces found, won't push forward
            self.setErrored("No face found.")
        return image

class FaceExtractorCascadePipe(FaceExtractorPipe):
    def __init__(self, cascadeXMLFilePath: str='./resources/face_detectors/facedetect_haarcascade_frontalface_default.xml', postProcessCallback=None):
        super().__init__(postProcessCallback=postProcessCallback)
        # check if file exists
        open(cascadeXMLFilePath,'r').close()
        self.face_cascade = CascadeClassifier(cascadeXMLFilePath)
    def getFaceBB(self, image: Image_Type, passThrough: PushPipe.PassThrough) -> Image_Type:
        gray = cvtColor(image, COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        if(len(faces)>0):
            # get largest face
            largest = (0,0,0,0)
            for (x,y,w,h) in faces:
                if(largest[-1]*largest[-2]<w*h):
                    largest = (x,y,w,h)
            (x,y,w,h) = largest
            rect = BoundingBox_twopoint(x,y,x+w,y+h)
            return rect
        else:
            # no faces found, won't push forward
            self.setErrored("No face found.")
        return image

class FaceExtractorDNNPipe(FaceExtractorPipe):
    def __init__(self, dnnModelFile="./resources/face_detectors/facedetect_dnn_res10_300x300_ssd_iter_140000_fp16.caffemodel", dnnConfigFile="./resources/face_detectors/facedetect_dnn_deploy.prototxt", confidenceThreshold = .6, postProcessCallback=None):
        super().__init__(postProcessCallback=postProcessCallback)
        # check files
        open(dnnConfigFile,'r').close()
        open(dnnModelFile,'r').close()
        self.net = dnn.readNetFromCaffe(dnnConfigFile, dnnModelFile)
        self.confidenceThreshold = confidenceThreshold
    def getFaceBB(self, image: Image_Type, passThrough: PushPipe.PassThrough) -> Image_Type:
        height, width, channels = image.shape[0:3]
        assert channels == 3
        blob = dnn.blobFromImage(resize(image, (300,300)), 1.0, (300, 300), [104, 117, 123], False, False)
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
        largest = [1 if X>1 else X for X in largest]
        largest[0] *= width
        largest[2] *= width
        largest[1] *= height
        largest[3] *= height
        largest = [int(round(X)) for X in largest]
        if(largest[0]+largest[2]<1 or largest[1]+largest[3]<1):
            # no faces found, won't push forward
            self.setErrored("No face found.")
        else:
            rect = BoundingBox_twopoint(*largest)
            return rect
        return image