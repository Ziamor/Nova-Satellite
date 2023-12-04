import os
import time
import wave
import pyaudio
import socketio
import webrtcvad

class AudioRecorder:
    def __init__(self, format, channels, rate, frame_duration_ms, vad_aggressiveness):
        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk = int(rate * frame_duration_ms / 1000)
        self.vad = webrtcvad.Vad(vad_aggressiveness)
        self.frames = []
        self.is_recording = False
        self.last_voice_detected_time = None

    def start_recording(self):
        self.is_recording = True
        self.last_voice_detected_time = time.time()

    def stop_recording(self):
        self.is_recording = False
        self.save_recording()
        self.frames.clear()

    def save_recording(self):
        filepath = os.path.join(os.path.dirname(__file__), 'recording.wav')
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
        print("Recording saved")

    def process_audio_data(self, data):
        if self.vad.is_speech(data, self.rate):
            self.last_voice_detected_time = time.time()
            self.frames.append(data)