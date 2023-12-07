import pyaudio

class AudioStream:
    def __init__(self, format=pyaudio.paInt16, channels=1, rate=16000, chunk=1600):
        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False

    def start_stream(self):
        self.stream = self.audio.open(format=self.format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)
        self.is_recording = True

    def read_data(self):
        return self.stream.read(self.chunk, exception_on_overflow=False)

    def stop_stream(self):
        self.is_recording = False
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()