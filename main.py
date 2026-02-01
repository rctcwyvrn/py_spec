from manim import *
import sys
import subprocess
import scipy.fftpack as fft 
from scipy.io import wavfile
from scipy.signal.windows import hann
import numpy as np
import multiprocessing
import math

IN_FILENAME = "/home/lily/Documents/draft-1.wav"
# IN_FILENAME = "/home/lily/Documents/test.wav"

NB_BITS = 16
FRAME_RATE= 10

BUMP = 10
WORKERS = 16

MAX_DB = 150
MIN_DB = 50
BUMP = 0.5

YOLO_TRUNCATION = 100

def fft_worker(frame):
    window = hann(len(frame))
    fft_data = abs(fft.fft(window * frame)) # calculate fourier transform (complex numbers list)
    fft_truncated = fft_data[:YOLO_TRUNCATION] # lmao
    fft_max_capped = [MAX_DB if x > MAX_DB else x for x in fft_truncated]
    fft_min_bumped = [MIN_DB if x < MIN_DB else x for x in fft_max_capped]
    fft_normalized = fft_truncated / max(fft_min_bumped)
    fft_boosted = fft_normalized + BUMP
    return fft_boosted

def load_audio():
    sample_rate, x = wavfile.read(IN_FILENAME)
    samples = x.T[0] / (float(2 ** NB_BITS)) # normalize

    # samples is a normalized list of frequencies, sampled at sample_rate/second
    # we want each fft to capture a certain # of seconds of sample. 
    # so we want each FRAME_RATE # of frames to capture sample_rate # of frequencies
    # so each frame of the animation contains sample_rate/frame_rate # of frequencies
    # and the total # of frames is frame_rate * song length in seconds
    # song length in seconds = # of frequency measurements/sample_rate


    song_length = int(len(samples) / sample_rate)
    frames = []
    frame_len = int(sample_rate / FRAME_RATE)
    # print(sample_rate, frame_len)
    
    for i in range(FRAME_RATE * song_length):
        frames.append(samples[i*frame_len:(i+1)*frame_len])

    runtime = math.floor(song_length)
    fft_dict = [None]*( FRAME_RATE * runtime)

    for i,frame in enumerate(frames):
        if(i%500 == 0):
            print("Frame #",i,"/",FRAME_RATE*runtime)
        processed_frame = fft_worker(frame)
        fft_dict[i] = processed_frame

    print("Finished fft ing ")
    return fft_dict

class CreateVisual(Scene):
    def construct(self):
        fft_dict = load_audio()
        def parametric_frame(frame):
            res = fft_dict[frame]
            res_len = len(res)
            def f(t):
                 scale = res[int(t)]
                 return (np.cos(t * (2 * PI) / res_len) * scale, 
                         np.sin(t * (2 * PI) / res_len) * scale, 
                         0)
            return ParametricFunction(f, t_range=(0,res_len-1,1)).scale(3)
        parametrics = [parametric_frame(frame) for frame in range(len(fft_dict))]
        p = parametrics[0]
        self.add(p)
        for i in range(1, len(parametrics)):
            self.play(ChangeSpeed(Transform(p, parametrics[i]), speedinfo={0:FRAME_RATE}))
