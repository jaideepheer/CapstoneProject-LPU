def rect_to_boundingbox(rect):
	# take a bounding box and convert it
	# to the format (x, y, width, height)
	x = rect.left()
	y = rect.top()
	w = rect.right() - x
	h = rect.bottom() - y
	# return a tuple of (x, y, w, h)
	return (x, y, w, h)

