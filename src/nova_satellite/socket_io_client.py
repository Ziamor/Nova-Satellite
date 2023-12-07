import socketio

class SocketIOClient:
    def __init__(self, url, socketio_path, event_callbacks=None):
        self.client = socketio.Client()
        self.url = url
        self.socketio_path = socketio_path
        self.event_callbacks = event_callbacks or {}
        self.setup_events()

    def setup_events(self):
        self.client.on('connect', self.on_connect)
        self.client.on('disconnect', self.on_disconnect)
        for event_name, callback in self.event_callbacks.items():
            self.client.on(event_name, callback)

    def on_connect(self):
        print("Connected to the server")

    def on_disconnect(self):
        print("Disconnected from the server")

    def connect(self):
        print(f"Connecting to {self.url}/{self.socketio_path}...")
        self.client.connect(self.url, socketio_path=self.socketio_path)

    def disconnect(self):
        self.client.disconnect()

    def wait(self):
        self.client.wait()