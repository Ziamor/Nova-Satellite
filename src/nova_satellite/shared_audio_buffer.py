class SharedAudioBuffer:
    def __init__(self, cache_size=10):
        self.frame_cache = []
        self.cache_size = cache_size
        self.frame_id = 0

    def update(self, data):
        if len(self.frame_cache) >= self.cache_size:
            self.frame_cache.pop(0)
        self.frame_cache.append({'frame_id': self.frame_id, 'data': data})
        self.frame_id += 1

    def read(self):
        return self.frame_cache[-1] if self.frame_cache else None

    def get_cached_frames_since(self, frame_id):
        return [frame for frame in self.frame_cache if frame['frame_id'] >= frame_id]