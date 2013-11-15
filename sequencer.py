from PySide import QtGui, QtCore
from util import SAMPLE_RATE, norm_time, norm_frequency, LogSlider, compose
import pyaudio
from functools import partial
import numpy as N
from bassdrum import BassDrum
from snaredrum import SnareDrum
from matplotlib import pyplot as P

class Drum:
    def __init__(self,drum_sound):
        self.drum_sound = drum_sound
        self.enabled = True
        self.beats = tuple(
            Beat(enabled = False) for beat in range(Sequencer.UNITS)
        )
    def get_beat(self,beat_index):
        return self.beats[beat_index]

    def is_enabled(self):
        return self.enabled

    def set_enabled(self,state):
        self.enabled = state

    def get_drum_sound(self):
        return self.drum_sound

class Beat:
    def __init__(self,amplitude=1.0,enabled=True):
        self.amplitude = amplitude
        self.enabled = enabled

    def get_amplitude(self):
        return self.amplitude

    def set_amplitude(self,amplitude):
        self.amplitude = amplitude

    def is_enabled(self):
        return self.enabled

    def set_enabled(self,state):
        self.enabled = state
        
class Sequencer:
    UNITS = 16
    def __init__(
        self,
        tempo=100.0
    ):
        self.spm = self.bpm_to_spm(tempo)
        self.stream = pyaudio.PyAudio().open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=SAMPLE_RATE,
            output=True,
            stream_callback=self.callback,
            frames_per_buffer=10000
        )
        self.position = 0
        self.drums = []

    def callback(self,in_data,frame_count,time_info,status):
        wave_form = N.zeros(frame_count)
        for beat, interval in enumerate(
            N.mod(
                N.arange(
                    offset,
                    offset+frame_count
                ),
                self.spm
            ) for offset in (
                self.position + self.spm - self.spm * beat / self.UNITS
                for beat in range(self.UNITS)
            )
        ):
            for drum in self.drums:
                if drum.is_enabled() and drum.get_beat(beat).is_enabled():
                    wave_form=(
                        wave_form
                        + (
                            drum.get_beat(beat).get_amplitude()
                            * drum.get_drum_sound().get_frames(interval)
                        )
                    )        
        self.position=(self.position+frame_count)%self.spm
        return (
            wave_form.astype(N.float32).tostring(),
            pyaudio.paContinue if self.stream.is_active() else pyaudio.paComplete
        )

    def add_drum(self,drum):
        self.drums.append(drum)

    # beats per minute to samples per measure
    @staticmethod
    def bpm_to_spm(bpm):
        return int(
            round(
                1.0 / bpm * 60.0 * SAMPLE_RATE * 4 # samples per measure
            )
        )

    # vice versa
    @staticmethod
    def spm_to_bpm(spm):
        return 1.0 / spm / 60.0 / SAMPLE_RATE / 4 # beats per minutes
        
    def set_bpm(self,bpm):
        old_spm = self.spm
        new_spm = self.bpm_to_spm(bpm)
        self.position = int(
            round(
                float(self.position) / old_spm * new_spm
            )
        )
        self.spm = new_spm

    def get_bpm(self):
        return self.spm_to_bpm(self.spm)

    def start(self):
        self.stream.start_stream()

    def stop(self):
        self.stream.stop_stream()
        self.position = 0

class SequencerWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.sequencer = sequencer = Sequencer()
        self.setLayout(QtGui.QVBoxLayout())

        start_button = QtGui.QPushButton('start')
        stop_button = QtGui.QPushButton('stop')
        
        start_button.clicked.connect(sequencer.start)
        stop_button.clicked.connect(sequencer.stop)
        
        start_button.clicked.connect(
            partial(
                start_button.setEnabled,
                False
            )
        )
        stop_button.clicked.connect(
            partial(
                stop_button.setEnabled,
                False
            )
        )
        
        start_button.clicked.connect(
            partial(
                stop_button.setEnabled,
                True
            )
        )
        stop_button.clicked.connect(
            partial(
                start_button.setEnabled,
                True
            )
        )

        start_button.setEnabled(True)
        stop_button.setEnabled(False)

        tempo_slider = QtGui.QSlider()
        tempo_slider.setRange(40,200)
        tempo_slider.setValue(int(sequencer.get_bpm()))
        tempo_slider.valueChanged.connect(
            compose(
                sequencer.set_bpm,
                float
            )            
        )

        control_layout = QtGui.QHBoxLayout()
        control_layout.addWidget(start_button)
        control_layout.addWidget(stop_button)
        control_layout.addStretch()
        control_layout.addWidget(QtGui.QLabel('tempo'))
        control_layout.addWidget(tempo_slider)

        self.layout().addLayout(control_layout,0)

    def add_drum(self,drum):
        seq = self.sequencer
        seq.add_drum(drum)
        drum_layout = QtGui.QHBoxLayout()
        self.layout().addLayout(drum_layout)
        for beat_index in range(seq.UNITS):
            beat = drum.get_beat(beat_index)

            beat_layout = QtGui.QVBoxLayout()
            drum_layout.addLayout(beat_layout)
            
            amp_slider = LogSlider(-2,.5,beat.get_amplitude())
            amp_slider.logChanged.connect(beat.set_amplitude)

            beat_layout.addWidget(amp_slider,1)
            
            check_box = QtGui.QCheckBox()

            bool_to_check_state = {
                True:QtCore.Qt.Checked,
                False:QtCore.Qt.Unchecked
            }

            check_box.setCheckState(
                bool_to_check_state[beat.is_enabled()]
            )

            check_state_to_bool = {
                QtCore.Qt.Checked:True,
                QtCore.Qt.Unchecked:False
            }
            
            check_box.stateChanged.connect(
                compose(
                    beat.set_enabled,
                    check_state_to_bool.__getitem__
                )
            )
            
            beat_layout.addWidget(check_box,0)

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)

    wid = SequencerWidget()
    wid.setWindowTitle('Drum Machine')
    wid.add_drum(
        Drum(
            BassDrum()
        )
    )
    wid.add_drum(
        Drum(
            SnareDrum()
        )
    )
    wid.show()
    sys.exit(app.exec_())
