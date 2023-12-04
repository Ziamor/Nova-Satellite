import pyaudio
import socketio
import threading
import wave
import os
import webrtcvad
import time

# Audio stream and VAD configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
FRAME_DURATION_MS = 30  # Frame duration in ms for VAD (10, 20, or 30 ms)
CHUNK = int(RATE * FRAME_DURATION_MS / 1000)  # Number of frames per buffer

# Create a Socket.IO client
sio = socketio.Client()

# Global variables for recording state
is_recording = False
frames = []
vad = webrtcvad.Vad(1)  # Set aggressiveness level
last_voice_detected_time = None
SILENCE_TIMEOUT = 2  # Seconds of non-speech to stop recording

def connect():
    print("Connection established")
    start_audio_thread()

def wake_word_detected(data):
    global is_recording, last_voice_detected_time
    print(f"Wake word detected by model {data['model']} with score {data['score']}")
    is_recording = True
    last_voice_detected_time = time.time()

def stop_recording():
    global is_recording
    is_recording = False
    save_recording()
    frames.clear()

def save_recording():
    filepath = os.path.join(os.path.dirname(__file__), 'recording.wav')
    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    print("Recording saved")

def start_audio_thread():
    thread = threading.Thread(target=run)
    thread.start()

def run():
    global is_recording, last_voice_detected_time
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("Ready to detect wake word...")
    try:
        while True:
            data = stream.read(CHUNK)
            sio.emit('stream_audio', data)

            if is_recording:
                if vad.is_speech(data, RATE):
                    last_voice_detected_time = time.time()
                    frames.append(data)
                elif time.time() - last_voice_detected_time > SILENCE_TIMEOUT:
                    stop_recording()

    except Exception as e:
        print("Exception in sending data:", e)
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        print("Thread terminating...")

if __name__ == "__main__":
    sio.on('connect', connect)
    sio.on('wake_word_detected', wake_word_detected)
    sio.connect("http://localhost:5001")
    sio.wait()
