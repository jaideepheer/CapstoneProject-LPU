from typing import NamedTuple

# (left, top, width, height)
BoundingBox_onepoint = NamedTuple('BoundingBox_onepoint',[('left',int), ('top',int), ('width',int), ('height',int)])
# (left, top, right, bottom)
BoundingBox_twopoint = NamedTuple('BoundingBox_twopoint',[('left',int), ('top',int), ('right',int), ('bottom',int)])