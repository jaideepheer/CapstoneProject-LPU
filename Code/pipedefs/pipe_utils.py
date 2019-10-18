from .core_pipes import PushPipe
from typing import TextIO
import time

def printPassThroughStatistics(passThrough: PushPipe.PassThrough, outputStream: TextIO):
    totalTime = time.time()
    processTime = 0.0
    # Frame statistics
    outputStream.write("Frame Statistics\n")
    outputStream.write("Timings:\n")
    for X in passThrough.getExtrasHistory():
        pipe: PushPipe = X['Pipe_Reference']
        outputStream.write('%s --> %f [Avg: %f]\n'%(X['Pipe_Type'], X['Profile.Process_Time'], pipe.profile.total_process_time/pipe.profile.process_call_count))
        processTime += X['Profile.Process_Time']
    outputStream.writelines([
            'Process Time: %f\n'%processTime
        ])
    outputStream.write('Profiling Time: %f\n'%(time.time()-totalTime))
class PipeLineProfilingWrapper():
    def __init__(self, pipeline: PushPipe, outputStream: TextIO):
        self.pipeline = pipeline
        self.out = outputStream
        self.worst_efficiency = 1
    def push(self, data, PassThrough) -> PushPipe.PassThrough:
        totalTime = time.time()
        retVal = self.pipeline.push(data, PassThrough)
        pushTime = time.time() - totalTime
        processTime = 0.0
        # Frame statistics
        self.out.write("Frame Statistics\n")
        self.out.write("Timings:\n")
        for X in retVal.getExtrasHistory():
            pipe: PushPipe = X['Pipe_Reference']
            self.out.write('%s --> %f [Avg: %f]\n'%(X['Pipe_Type'], X['Profile.Process_Time'], pipe.profile.total_process_time/pipe.profile.process_call_count))
            processTime += X['Profile.Process_Time']
        efficiency = processTime/pushTime
        self.worst_efficiency = min(self.worst_efficiency, efficiency)
        self.out.writelines([
            'Total Time: %f\n'%pushTime,
            'Process Time: %f\n'%processTime,
            'Wasted Time: %f\n'%(pushTime-processTime),
            'Efficiency: %f\n'%efficiency,
            'Worst Efficiency: %f\n'%self.worst_efficiency
        ])
        self.out.write('Profiling Time: %f\n'%(time.time()-totalTime-pushTime))
        return retVal