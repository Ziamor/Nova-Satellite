import pyaudio
import time
import sys
from nova_satellite.socket_io_client import SocketIOClient
from nova_satellite.audio_stream import AudioStream
from nova_satellite.audio_recorder import AudioRecorder
from nova_satellite.shared_audio_buffer import SharedAudioBuffer

# Constants
FORMAT = pyaudio.paInt16
CHANNELS = 1 # Mono
RATE = 16000 # Sample rate in Hz
FRAME_DURATION_MS = 30  # Frame duration in ms
CHUNK = int(RATE * FRAME_DURATION_MS / 1000)
VAD_TIMEOUT = 3 # Seconds

class WakeWordService:
    def __init__(self, url, path):
        self.client = SocketIOClient(url, socketio_path=path, event_callbacks={
            'wake_word_detected': self.wake_word_detected
        })
        self.client.connect()
        self.is_wake_word_detected = False
        self.audio_recorder = None
        self.shared_audio_buffer = None

    def wake_word_detected(self, data):
        frame_id = data['frame_id']
        print(f"Wake word detected on frame {frame_id}")
        print(data)
        self.is_wake_word_detected = True    
        self.audio_recorder.start_recording()
        for frame in self.shared_audio_buffer.get_cached_frames_since(frame_id):
            self.audio_recorder.process_audio_data(frame['data'])

    def stream_audio(self, audio_buffer):
        frame = audio_buffer.read()
        if frame:
            self.client.client.emit('stream_audio', frame)

    def set_recorder_and_buffer(self, recorder, buffer):
        self.audio_recorder = recorder
        self.shared_audio_buffer = buffer

class CommandService:
    def __init__(self, url, path):
        self.client = SocketIOClient(url, socketio_path=path)
        self.client.connect()

    def stream_audio(self, audio_recorder, audio_buffer):
        frame = audio_buffer.read()
        if frame:
            audio_recorder.process_audio_data(frame['data'])
            self.client.client.emit('stream_audio', frame)
            if time.time() - audio_recorder.vad.last_voice_detected_time > VAD_TIMEOUT:
                audio_recorder.stop_recording()
                return False
        return True

def main():
    audio_stream = AudioStream(FORMAT, CHANNELS, RATE, CHUNK)
    audio_recorder = AudioRecorder(FORMAT, CHANNELS, RATE, FRAME_DURATION_MS, 3)
    shared_audio_buffer = SharedAudioBuffer()

    wake_word_service = WakeWordService('http://localhost', '/wake-word-detection')
    command_service = CommandService('http://localhost', '/command-processing')
    
    wake_word_service.set_recorder_and_buffer(audio_recorder, shared_audio_buffer)

    try:
        audio_stream.start_stream()
        while True:
            data = audio_stream.read_data()
            shared_audio_buffer.update(data)

            wake_word_service.stream_audio(shared_audio_buffer)
            if wake_word_service.is_wake_word_detected:
                continue_streaming = command_service.stream_audio(audio_recorder, shared_audio_buffer)
                if not continue_streaming:
                    wake_word_service.is_wake_word_detected = False
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        audio_stream.stop_stream()
        wake_word_service.client.disconnect()
        command_service.client.disconnect()

if __name__ == '__main__':
    main()
