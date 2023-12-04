import socketio

class SocketIOClient:
    def __init__(self, url, namespaces, wake_word_callback=None):
        self.client = socketio.Client()
        self.url = url
        self.namespaces = namespaces
        self.wake_word_callback = wake_word_callback
        self.setup_events()

    def setup_events(self):
        self.client.on('connect', self.on_connect)
        self.client.on('disconnect', self.on_disconnect)
        self.client.on('wake_word_detected', self.wake_word_detected)

    def on_connect(self):
        print("Connected to the server")

    def on_disconnect(self):
        print("Disconnected from the server")

    def wake_word_detected(self, data):
        print(f"Wake word detected: {data}")
        if self.wake_word_callback:
            self.wake_word_callback()

    def connect(self):
        self.client.connect(self.url, namespaces=self.namespaces)

    def disconnect(self):
        self.client.disconnect()

    def wait(self):
        self.client.wait()
