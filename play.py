#!/usr/bin/env python

from math import sqrt
import numpy as np
import serial
import pyaudio
import wave
import time
import sys
import numpy

use_serial = True
use_scale = True

files = (
    #'bing-a.wav',
    'guitar.wav',
    #'bing-c.wav',
    #'bassdrum.wav',
    #'snare.wav',
)

note_speeds = [s / 261.626 for s in [
    261.626, # C
    #277.183, # C#
    #293.665, # D
    #311.127, # D#
    329.628, # E
    #349.228, # F
    #369.994, # F#
    391.995, # G
    #415.305, # G#
    #440.000, # A
    #466.164, # Bb
    #493.883, # B
    523.251, # C
]]

def get_next_event():
    while True:
        if use_serial:
            line = serial.readline()
        else:
            line = raw_input()
        strings = line.split()
        if len(strings) != 2:
            continue
        return tuple(int(v) for v in line.split())

buffer = numpy.zeros(20000, dtype=float)
buffer16 = numpy.zeros(20000, dtype=np.int16)

def callback(in_data, frame_count, time_info, status):

    buffer[:] = 0
    for index, sample in enumerate(samples):
        volume = volumes[index]
        if volume == 0:
            continue
        position = positions[index]
        speed = speeds[index]
        for target_index in xrange(frame_count):
            if position >= len(sample):
                volumes[index] = 0
                break
            buffer[target_index] += sample[int(position)] * volume
            position += speed
        positions[index] = int(position)

    buffer16[:frame_count] = (buffer[:frame_count].clip(-1, 1) * 32767).astype(np.int16)
    return (buffer16.tostring(), pyaudio.paContinue)

if use_serial:
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

CHANNELS = 4
samples = [samples[0]] * CHANNELS

#positions = [9999999] * len(samples)
positions = [0] * len(samples)
volumes = [0] * len(samples)
speeds = [1.0] * len(samples)

p = pyaudio.PyAudio()

stream = p.open(
    format = p.get_format_from_width(2),
    channels = 1,
    rate = 44100,
    output = True,
    stream_callback = callback
)

stream.start_stream()

next_index = 0
print 'streaming'
while True:
    velocities = [sqrt(v) for v in get_next_event()]
    t = velocities[1] / float(velocities[0] + velocities[1])

    index = next_index
    next_index = (next_index + 1) % CHANNELS

    if use_scale:
        idx = int(t * len(note_speeds) * .9999)
        speed = note_speeds[idx]
        #print 'idx', idx
    else:
        speed = 1.0 + t

    positions[index] = 0
    print 't =', t, 'speed =', speed
    speeds[index] = speed
    volume = (velocities[0] + velocities[1]) * 1.5
    print volume
    volumes[index] = volume
    #print repr(velocities)

stream.stop_stream()
stream.close()

p.terminate()
