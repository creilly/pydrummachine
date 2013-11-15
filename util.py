from PySide import QtGui, QtCore
import numpy as N
from functools import partial

SAMPLE_RATE = 44100

def compose(func_1, func_2):
    """
    compose(func_1, func_2) -> function

    The function returned by compose is a composition of func_1 and func_2.
    That is, compose(func_1, func_2)(5) == func_1(func_2(5))
    """
    if not callable(func_1):
        raise TypeError("First argument to compose must be callable")
    if not callable(func_2):
        raise TypeError("Second argument to compose must be callable")

    def composition(*args, **kwargs):
        return func_1(func_2(*args, **kwargs))
    return composition

def norm_frequency(frequency):
    return frequency / float(SAMPLE_RATE)
def norm_time(time):
    return time * float(SAMPLE_RATE)
class LogSlider(QtGui.QSlider):
    logChanged = QtCore.Signal(float)
    def __init__(self,min,max,default):
        QtGui.QSlider.__init__(self)
        self.valueChanged.connect(
            compose(
                self.logChanged.emit,
                self._convert
            )
        )
        self.setOrientation(QtCore.Qt.Horizontal)
        self._min = min
        self._max = max
        self.setValue(
            int(
                round(
                    100. * (default - min) / (max - min)
                )
            )
        )
    def value(self):
        return self._convert(QtGui.QSlider.value(self))
    def _convert(self,value):
        return N.power(10,self._min + .01 * value * (self._max - self._min))