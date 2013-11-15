from PySide import QtGui, QtCore
from drumsound import DrumSound
import numpy as N

class BassDrum(DrumSound):
    BODY,POP,CLICK = 0,1,2
    COMPS = (BODY,POP,CLICK)
    CHIRP_HIGH,CHIRP_LOW,CHIRP_DUR,ENV_DUR,VOLUME,ENABLED = 0,1,2,3,4,5
    PARAMS = (CHIRP_HIGH,CHIRP_LOW,CHIRP_DUR,ENV_DUR,VOLUME,ENABLED)
    DEFAULTS = {
        BODY:{
            CHIRP_HIGH:2.4,
            CHIRP_LOW:1.9,
            CHIRP_DUR:-1,
            ENV_DUR:-1,
            VOLUME:-.2,
            ENABLED:True
        },
        POP:{
            CHIRP_HIGH:2.8,
            CHIRP_LOW:2.3,
            CHIRP_DUR:-1,
            ENV_DUR:-1.5,
            VOLUME:-1.3,
            ENABLED:True
        },
        CLICK:{
            CHIRP_HIGH:3.5,
            CHIRP_LOW:2.5,
            CHIRP_DUR:-1.6,
            ENV_DUR:-1.6,
            VOLUME:-1.7,
            ENABLED:True
        }
    }
    def __init__(self,params=DEFAULTS):
        for comp_params in params.values():
            for param in comp_params:
                if param is not self.ENABLED:
                    comp_params[param] = N.power(10.0,comp_params[param])
        DrumSound.__init__(self,params)
    def get_frames(self,time):
        wave_form = N.zeros(time.shape)
        for comp,param_dict in (
            (comp,self.params[comp])
            for comp in self.COMPS
            if self.params[comp][self.ENABLED]
        ):
            wave_form = (
                wave_form
                + (
                    param_dict[self.VOLUME]
                    * (
                        self.gaussian if comp is self.BODY else self.envelope
                    )(time,param_dict[self.ENV_DUR])
                    * self.chirp(
                        time,
                        *(
                            param_dict[param]
                            for param in (
                                self.CHIRP_HIGH,
                                self.CHIRP_LOW,
                                self.CHIRP_DUR
                            )
                        )
                    )
                )
            )
        return wave_form

class BassDrumWidget(QtGui.QWidget):
    RANGES = {
        BassDrum.CHIRP_HIGH:(2,4),
        BassDrum.CHIRP_LOW:(1,3),
        BassDrum.CHIRP_DUR:(-2,0),
        BassDrum.ENV_DUR:(-2,0),
        BassDrum.VOLUME:(-2,0)
    }
    def __init__(self,bass_drum):
        QtGui.QWidget.__init__(self)

        self.setLayout(QtGui.QHBoxLayout())

        sliders=self.sliders={
            comp:{
                param:LogSlider(
                    *(
                        self.RANGES[param]
                        + [bass_drum.get_parameter(comp,param)]
                    )
                ) for param in self.PARAMS
            } for comp in self.COMPS
        }
        checks=self.checks={
            comp:QtGui.QCheckBox()
            for comp in self.COMPS
        }
        for comp in self.COMPS:            
            form = QtGui.QFormLayout()
            form.addRow(
                QtGui.QLabel(
                    {
                        self.BODY:'body',
                        self.POP:'pop',
                        self.CLICK:'click'
                    }[comp]
                )
            )
            check = self.checks[comp]
            check.setState(self.params[comp][self.CHECKED])
            check.stateChanged.connect(
                compose(
                    partial(
                        bass_drum.set_param,
                        comp,
                        bass_drum.ENABLED
                    ),
                    bool
                )
            )
            form.addRow(
                'enable',
                check
            )
            for param in self.PARAMS:
                if param is self.ENABLED: continue
                slider = sliders[comp][param]
                slider.logChanged.connect(
                    partial(
                        bass_drum.set_param,
                        comp,
                        param
                    )
                )
                form.addRow(
                    {
                        self.CHIRP_HIGH:'high freq',
                        self.CHIRP_LOW:'low freq',
                        self.CHIRP_DUR:'chirp dur',
                        self.ENV_DUR:'env dur',
                        self.VOLUME:'volume'
                    }[param],
                    slider
                )
            self.layout().addLayout(form)