from util import norm_time, norm_frequency
import numpy as N

class DrumSound:
    def __init__(self,params):
        self.params=params
    def set_param(self,comp,param,value):
        self.params[comp][param] = value
    def get_param(self,comp,param):
        return self.params[comp][param]
    def chirp(self,time,start,stop,decay):
        return N.sin(
            2. * N.pi * (
                norm_frequency(stop)
                + (
                    norm_frequency(start-stop)
                    * N.exp(-1. * time / norm_time(decay))
                )
            ) * time
        )
    def envelope(self,time,decay):
        return N.exp(-1. * time / norm_time(decay))
    def gaussian(self,time,decay):
        return N.exp(
            -1. * N.power(time / norm_time(decay), 2)
        )