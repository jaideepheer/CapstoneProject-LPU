from dlib import rectangle as dlib_rectangle
from ..utils.typedefs import BoundingBox_onepoint, BoundingBox_twopoint

def dlibrect_to_BoundingBox_onepoint(rect: dlib_rectangle) -> BoundingBox_onepoint:
	# take a bounding box and convert it
	# to the format (left, top, width, height)
	x = rect.left()
	y = rect.top()
	w = rect.right() - x
	h = rect.bottom() - y
	# return a tuple of (left, top, w, h)
	return BoundingBox_onepoint(x, y, w, h)
def dlibrect_to_BoundingBox_twopoint(rect: dlib_rectangle) -> BoundingBox_twopoint:
	return BoundingBox_twopoint(rect.left(), rect.top(), rect.right(), rect.bottom())

def BoundingBox_twopoint_to_dlibrect(rect: BoundingBox_twopoint) -> dlib_rectangle:
	return dlib_rectangle(rect.left,rect.top,rect.right,rect.bottom)
def BoundingBox_onepoint_to_dlibrect(rect: BoundingBox_onepoint) -> dlib_rectangle:
	return dlib_rectangle(rect.left,rect.top,rect.left+rect.width,rect.top+rect.height)
