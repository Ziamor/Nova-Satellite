import pyaudio
from nova_satellite.audio_recorder import AudioRecorder
from nova_satellite.audio_stream import AudioStreamThread
from nova_satellite.socket_io_client import SocketIOClient

FORMAT = pyaudio.paInt16
CHANNELS = 1 # Mono
RATE = 16000 # Sample rate in Hz
FRAME_DURATION_MS = 30  # Frame duration in ms, needs to be either 10, 20, or 30 ms for VAD to work properly
VAD_MODE = 1 # 0 to 3, 0 is the least aggressive about filtering out non-speech, 3 is the most aggressive

def main():
    recorder = AudioRecorder(pyaudio.paInt16, CHANNELS, RATE, FRAME_DURATION_MS, VAD_MODE)
    
	# Initialize SocketIOClient with a callback to start recording
    socket_client = SocketIOClient('http://localhost', ['/wake-word-detection'], wake_word_callback=recorder.start_recording)
    socket_client.connect()

    # Initialize and start the AudioStreamThread
    audio_interface = pyaudio.PyAudio()
    stream = audio_interface.open(format=recorder.format, channels=recorder.channels, rate=recorder.rate, input=True, frames_per_buffer=recorder.chunk)
    audio_thread = AudioStreamThread(recorder, audio_interface, stream, socket_client.client)
    audio_thread.start()

    try:
        socket_client.wait()
    except KeyboardInterrupt:
        print("Application interrupted, cleaning up...")
        cleanup(audio_thread, socket_client)

def cleanup(audio_thread, socket_client):
    audio_thread.stop()
    audio_thread.join()
    socket_client.disconnect()

if __name__ == '__main__':
    main()

