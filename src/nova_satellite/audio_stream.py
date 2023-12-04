import threading
import time

class AudioStreamThread(threading.Thread):
    def __init__(self, recorder, audio_interface, stream, sio):
        super().__init__()
        self.recorder = recorder
        self.audio_interface = audio_interface
        self.stream = stream
        self.sio = sio

    def run(self):
        print("Ready to detect wake word...")
        try:
            while True:
                data = self.stream.read(self.recorder.chunk)
                # Emit audio data to server...
                self.sio.emit('stream_audio', data)

                if self.recorder.is_recording:
                    self.recorder.process_audio_data(data)
                    if time.time() - self.recorder.last_voice_detected_time > 2:  # SILENCE_TIMEOUT
                        self.recorder.stop_recording()

        except Exception as e:
            print("Exception in sending data:", e)
        finally:
            self.stream.stop_stream()
            self.stream.close()
            self.audio_interface.terminate()
            print("Thread terminating...")
            
    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio_interface.terminate()
        print("Thread terminating...")