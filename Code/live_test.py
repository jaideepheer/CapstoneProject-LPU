import cv2
from face.face_feature_extractors import face_feature_extractor_dlib68
from face.face_detectors import face_detector_dlib
from emotion.emotion_extractors import emotion_extractor_oarriaga

def getCroppedImage(image, rectangle):
    return image[rectangle.top():rectangle.bottom(), rectangle.left():rectangle.right()]

face_detector = face_detector_dlib()
face_feature = face_feature_extractor_dlib68()
emotion_extractor = emotion_extractor_oarriaga()
stream = cv2.VideoCapture(0)
while(True):
    ret, img = stream.read()
    faceRect = face_detector.getFaceBoxLocation(img)
    faceImg = getCroppedImage(img, faceRect)
    features = face_feature.getFaceFeaturePoints(img, faceRect)
    print(faceRect)
    emotions = emotion_extractor.getFaceEmotionDistribution(faceImg)
    print(emotions)
    for (x, y) in features:
	    cv2.circle(img, (x, y), 1, (0, 0, 255), -1)
    cv2.imshow('img',img)
    cv2.imshow('face', faceImg)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
stream.release()
cv2.destroyAllWindows()