class WindowClosedException(Exception):
    def __init__(self):
        super().__init__("Interaction not possible due to stale window")
