from easygui import fileopenbox
from gui.custom_subclasses import ynbox, choicebox
from video.video_utils import saveVideoThumbnail
from utils.gui_util import centerWindow
from utils.memory_util import clearGPUMemory
from utils.typedefs import VideoReport, AudioReport
import tempfile
from workers import VideoWorker, AudioWorker
from gui.tkinter.processing_windows import VideoProcessingWindow, AudioProcessingWindow
from gui.tkinter.final_report_window import ReportWindow
import tkinter as tk

# render main menu
def mainMenu():
    # loop to get correct file path
    while(True):
        msg ="Welcome to Speech Analyser, please select a video file for processing.\nPlease select an option to proceed."
        title = "Main Menu"
        choices = ["Select a video file", "Exit"]
        choice = choicebox(msg, title, choices)
        if(choice == choices[0]):
            r = fileopenbox(msg="Please choose a video file.", title="Video File Selector", filetypes=[["*.mp4","*.mkv","*.flv","Video Files"]])
            if r == None:
                # video selection cancelled
                continue
            return r
        elif choice == choices[1] or choice is None:
            return 0

# show confirm video dialog with generated thumbnail
def confirmVideo(filePath):
    # save thumbnail in temporary dir.
    with tempfile.TemporaryDirectory() as tmpdirname:
        temp=tmpdirname+"/tmp_thumb"
        saveVideoThumbnail(filePath, temp)
        choice = ynbox("Are you sure you want to start processing this video?", image=temp)
    return choice

# select processing mode
def processFileModeSelect(filePath):
    choice = choicebox(
        msg="""
There are two types of processing available, video and audio.

 - Video processing finds expressional sentiment using the video frames of the file.
 - Audio processing finds the contextual sentiment using the text transcript extracted from the audio data of the file. It also calculates the approximate total word count and presents a bar chart for the number of words spoken with respect to time.
        Please choose the processing mode.""",
        title="Choose Processing Mode",
        choices=[
            "Video Only",
            "Audio Only",
            "Both"
        ],
        preselect=2
    )
    if choice is None:
        return 0
    else:
        return choice

# perform both processing based on the mode selected by user
def processFile(filePath, mode):
    # calc flags
    doVideo = False
    doAudio = False
    if mode == "Both": 
        doVideo = True
        doAudio = True
    elif mode == "Video Only": doVideo = True
    elif mode == "Audio Only": doAudio = True

    vidReport = None
    audReport = None

    if doVideo:
        vidGUI = tk.Tk()
        vidGUI.title("Video Processing")
        vidGUI.geometry("1024x600")
        centerWindow(vidGUI)
        vidWorker = VideoWorker(filePath,VideoProcessingWindow(vidGUI))
        # construct video processing pipeline
        print("Creating video processing worker...")
        print("Running video processing worker.")
        vidWorker.start()
        vidGUI.mainloop()
        print("Video processing done.")
        if doAudio:
            if ynbox(
                msg="Video processing has finished, the program is configured to proceed to audio processing now. Do you wish to continue for audio processing?",
                title="Audio Processing Confirmation"
            ) == False:
                print("Audio processing skipped.")
                doAudio = False
        print("Waiting for video worker to terminate.")
        vidWorker.join()
        print("Video worker terminated.")
        # GPU memory must be cleared by the main thread
        clearGPUMemory()
        res = vidWorker.getFinalResult()
        vidReport = VideoReport(
            res.get('OverallEmotionChart', None),
            res.get('DominantEmotionFaceFrame', None),
            res.get('DominantEmotionFrame', None),
            res.get('DominantEmotion', 'None'),
            res.get('Total_Frames_Processed', -1),
            res.get('FramesWithFace', 0)
        )
    if doAudio:
        audioGUI = tk.Tk()
        audioGUI.title("Audio Processing")
        audioGUI.geometry("1024x600")
        centerWindow(audioGUI)
        audioWorker = AudioWorker(filePath,AudioProcessingWindow(audioGUI))
        # construct audio processing pipeline
        print("Creating audio processing worker...")
        print("Running audio processing worker.")
        audioWorker.start()
        audioGUI.mainloop()
        print("Audio processing done.")
        print("Waiting for audio worker to terminate.")
        audioWorker.join()
        print("Audio worker terminated.")
        # GPU memory must be cleared by the main thread
        clearGPUMemory()
        res = audioWorker.getFinalResult()
        audReport = AudioReport(
            res.get('WordCountChart', None),
            res.get('SentimentChart', None),
            res.get('Total_WordCount', 0),
            res.get('TotalTimeProcessed', 0),
            res.get('WordsPerSecond', 0)
        )
    return vidReport, audReport

def showReport(vidReport, audReport):
    root = tk.Tk()
    win = ReportWindow(root, audReport, vidReport)
    root.geometry("1024x600")
    centerWindow(root)
    root.mainloop()
    return win.didUserChooseExit()

# handle gui controll flow
def run():
    run_func = mainMenu
    args = {}
    local_vars = {}
    while(True):
        retval = run_func(*args)
        args = {}
        # main menu
        if run_func is mainMenu:
            if retval == 0:
                break # main menu closed/exit
            elif isinstance(retval,str):
                local_vars['filepath'] = retval
                run_func = confirmVideo
                args = [retval]
        # confirm video dialog
        elif run_func is confirmVideo:
            if retval:
                run_func = processFileModeSelect
                args = [local_vars['filepath']]
            else:
                run_func = mainMenu
        # process file mode select dialog
        elif run_func is processFileModeSelect:
            if retval == 0:
                # mode select cancelled
                run_func = mainMenu
            else:
                # mode select done
                local_vars['mode'] = retval
                run_func = processFile
                args = [local_vars['filepath'],retval]
        elif run_func is processFile:
            run_func = showReport
            args = retval
        elif run_func is showReport:
            if retval:
                print("Exiting.")
                break # user selected to exit from report window
            else:
                run_func = mainMenu
        else:
            #TODO: show gui error
            break
run()