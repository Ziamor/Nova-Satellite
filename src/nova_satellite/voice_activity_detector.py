import webrtcvad
import time

class VoiceActivityDetector:
    def __init__(self, rate, vad_aggressiveness):
        self.vad = webrtcvad.Vad(vad_aggressiveness)
        self.rate = rate
        self.is_speech = False
        self.last_voice_detected_time = None

    def process_audio_data(self, data):
        self.is_speech = self.vad.is_speech(data, self.rate)
        if self.is_speech:
            self.last_voice_detected_time = time.time()
        return self.is_speech