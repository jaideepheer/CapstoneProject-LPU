from abc import ABCMeta, abstractmethod
from typing import List, Generic, TypeVar, Callable, Any, Dict
from types import MappingProxyType
from dataclasses import dataclass, field
from enum import Enum
import time

PushPipe_T_IN = TypeVar('PushPipe_T_IN')
PushPipe_T_OUT = TypeVar('PushPipe_T_OUT')
class PushPipe(Generic[PushPipe_T_IN, PushPipe_T_OUT], metaclass=ABCMeta):
    @dataclass
    class PipeProfile:
        last_process_time_sec: float = 0
        total_process_time: int = 0
        process_call_count: int = 0
    @dataclass
    class PassThrough:
        _extras: Dict[str, Any] = field(default_factory=dict)
        _extras_history: List[MappingProxyType] = field(default_factory=list)
        _GLOBALS: Dict[str, Any] = field(default_factory=dict)
        def getGlobals(self):
            return self._GLOBALS
        def getExtrasHistory(self):
            return (*self._extras_history,)
        def getCurrentExtras(self):
            return self._extras
        def __PrepareNewExtras__(self):
            self._extras = dict()
            self._extras_history.append(MappingProxyType(self._extras))
    class Result(Enum):
        ERROR = False
        SUCCESS = True
    def __init__(self, postProcessCallback: Callable[['PushPipe.Result', PushPipe_T_OUT, Any, 'PushPipe.PassThrough', 'PushPipe.PipeProfile'], None] = None):
        self.children: List[PushPipe[PushPipe_T_OUT,Any]] = []
        self.processCallback = postProcessCallback
        self.result = PushPipe.Result.SUCCESS
        self.error = None
        self.profile = PushPipe.PipeProfile(0,0,0)
    def connect(self, *pipes: 'PushPipe[PushPipe_T_OUT]') -> 'PushPipe[PushPipe_T_IN, PushPipe_T_OUT]':
        self.children.extend(pipes)
        return self
    def setErrored(self, errorData: Any):
        self.result = PushPipe.Result.ERROR
        self.error = errorData
    def push(self, data: PushPipe_T_IN, PassThrough: 'PushPipe.PassThrough') -> 'PushPipe.PassThrough':
        # prepare current extras
        PassThrough.__PrepareNewExtras__()
        curExtras = PassThrough.getCurrentExtras()
        curExtras['Pipe_Reference'] = self
        curExtras['Pipe_Type'] = type(self)
        curExtras['Process_Input'] = data
        # start profiling
        self.profile.process_call_count += 1
        #process
        self.process_time = time.time()
        output = self.process(data, PassThrough)
        self.process_time = time.time() - self.process_time
        # update profiling data
        curExtras['Process_Output'] = output
        curExtras['Profile.Process_Time'] = self.process_time
        curExtras['Process_Result'] = self.result
        curExtras['Process_Error'] = self.error
        self.profile.last_process_time_sec = self.process_time
        self.profile.total_process_time += self.process_time
        # execute callback
        if(self.processCallback is not None):
            self.processCallback(self.result, output, self.error, PassThrough, self.profile)
        # propogate pipe push to next pipes
        if(self.result == PushPipe.Result.SUCCESS):
            # if processing resulted in no errors, push processed output data to connected pipes
            # TODO: make pupe push multi-threaded
            for c in self.children:
                c.push(output, PassThrough)
        else:
            # processing was unsuccessfull, skip propogation and reset result
            # check PassThrough extras for error data, 'Process_Result' and 'Process_Error'
            self.error = ""
            self.result = PushPipe.Result.SUCCESS
        return PassThrough
    # Implement this function
    # Use self.setErrored(errorData) to signal that processing has failed.
    @abstractmethod
    def process(self, data: PushPipe_T_IN, passThrough: 'PushPipe.PassThrough') -> PushPipe_T_OUT:
        pass

from types import MethodType
class ProcessPushPipe(PushPipe[PushPipe_T_IN, PushPipe_T_OUT]):
    def __init__(self, processingFunc: Callable[['ProcessPushPipe', PushPipe_T_IN, PushPipe.PassThrough], PushPipe_T_OUT], postProcessCallback=None):
        super().__init__(postProcessCallback=postProcessCallback)
        self.process = MethodType(processingFunc, self)
    def process(self, data, passThrough):
        return super().process(data, passThrough)