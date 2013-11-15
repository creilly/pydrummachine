from util import norm_time, norm_frequency
from drumsound import DrumSound
import numpy as N
class SnareDrum(DrumSound):
    def __init__(self):
        DrumSound.__init__(self,{})
    def get_frames(self,time):
        return N.random.rand(*time.shape) * self.envelope(time,.1)