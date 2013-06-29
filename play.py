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
    note, velocity = line.split()
    note = int(note)
    velocity = int(velocity)
    return (note, velocity)

buffer = numpy.zeros(20000, dtype=float)
buffer16 = numpy.zeros(20000, dtype=np.int16)

def callback(in_data, frame_count, time_info, status):

    buffer[:] = 0
    for index, sample in enumerate(samples):
        position = positions[index]
        if position < len(sample):
            count = min(frame_count, len(sample) - position)
            buffer[:count] += sample[position : position + count] * volumes[index]
            positions[index] += frame_count
        else:
            volumes[index] = 0
    buffer16[:frame_count] = (buffer[:frame_count].clip(-1, 1) * 32767).astype(np.int16)
    return (buffer16.tostring(), pyaudio.paContinue)


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
    b = a.astype(float) / 32768.0
    samples.append(b)
    wf.close()

positions = [9999999] * len(samples)
volumes = [0] * len(samples)

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
    note, velocity = get_next_event()
    positions[note] = 0
    volume = max(.2, min(velocity * .1, 5.0)) * .2
    volumes[note] = volume
    print note, velocity, volume

stream.stop_stream()
stream.close()

p.terminate()
