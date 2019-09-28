print("Installing Indian accent acoustic model for speech-recognition.")
import speech_recognition as sr
from os import path, mkdir
import shutil
sr_dir = path.dirname(sr.__file__)
in_dir = path.join(sr_dir,"pocketsphinx-data")
print('Extracting cmusphinx-en-in-5.2.tar to speech-recognition library folder. (%s)'%in_dir)
shutil.unpack_archive('cmusphinx-en-in-5.2.tar.gz',in_dir)
print('Indian accent acoustic model installed.')
