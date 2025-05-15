import datetime
import time

class Timer:
    def __init__(self, interval):
        self.last_datetime = None
        self.interval = interval

    def fire(self):
        now = datetime.datetime.now()

        if self.last_datetime is None or now - self.last_datetime > self.interval:
            if self.last_datetime is None:
                self.last_datetime = now

            self.last_datetime += self.interval

            return True

        return False
        
