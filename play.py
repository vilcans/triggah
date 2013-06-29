#!/usr/bin/env python

import serial
import pyaudio
import wave
import time
import sys

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

serial = serial.Serial('/dev/ttyACM0', 9600)

wf = wave.open(sys.argv[1], 'rb')
p = pyaudio.PyAudio()

def get_value():
    while True:
        line = serial.readline()
        try:
            return int(line)
        except ValueError:
            pass


def callback(in_data, frame_count, time_info, status):
    #print frame_count, time_info, status
    #data = wf.readframes(frame_count)
    #global position
    #clip = sample_data[position : position + frame_count]
    #position += frame_count
    #clip = wf.readframes(frame_count)

    global position
    expected_bytes = bytes_per_frame * frame_count
    clip = sample[
        position * bytes_per_frame : (position + frame_count) * bytes_per_frame
    ]
    if len(clip) < expected_bytes:
        #clip += '\0' * (expected_bytes - len(clip))
        clip = '\0' * (frame_count * bytes_per_frame)
    position += frame_count
    return (clip, pyaudio.paContinue)

sample = wf.readframes(100000)
bytes_per_frame = wf.getsampwidth() * wf.getnchannels()
print 'sample width', wf.getsampwidth()
print 'channels', wf.getnchannels()
print 'frame rate', wf.getframerate()
wf.close()

stream = p.open(
    format = p.get_format_from_width(wf.getsampwidth()),
    channels = wf.getnchannels(),
    rate = wf.getframerate(),
    output = True,
    stream_callback = callback
)

#sample_data = wf.readframes(100000)
position = 0

stream.start_stream()

print 'streaming'
while True:
    v = get_value()
    position = 0
#while stream.is_active():
#    time.sleep(0.1)
print 'done streaming'

stream.stop_stream()
stream.close()

p.terminate()
