#!/usr/bin/env python

import numpy as np
import serial
import pyaudio
import wave
import time
import sys
import numpy

files = (
    'bassdrum.wav',
    'snare.wav',
)

def get_next_event():
    line = serial.readline()
    char = line[0]
    return ord(char) - 48

buffer = numpy.zeros(20000, dtype=np.int16)

def callback(in_data, frame_count, time_info, status):

    buffer[:] = 0
    for index, sample in enumerate(samples):
        position = positions[index]
        if position < len(sample):
            count = min(frame_count, len(sample) - position)
            buffer[:count] += sample[position : position + count]

        positions[index] += frame_count
    return (buffer.tostring(), pyaudio.paContinue)


serial = serial.Serial('/dev/ttyACM0', 9600)

samples = []
for file in files:
    wf = wave.open(file, 'rb')
    assert wf.getsampwidth() == 2
    assert wf.getnchannels() == 1
    #print 'sample width', wf.getsampwidth()
    #print 'channels', wf.getnchannels()
    #print 'frame rate', wf.getframerate()

    data = wf.readframes(100000)
    a = np.fromstring(data, dtype=np.int16)
    a.newbyteorder('>')
    samples.append(a)
    wf.close()

positions = [9999999] * len(samples)

p = pyaudio.PyAudio()

stream = p.open(
    format = p.get_format_from_width(2),
    channels = 1,
    rate = 44100,
    output = True,
    stream_callback = callback
)

stream.start_stream()

print 'streaming'
while True:
    v = get_next_event()
    positions[v] = 0
#while stream.is_active():
#    time.sleep(0.1)
print 'done streaming'

stream.stop_stream()
stream.close()

p.terminate()
