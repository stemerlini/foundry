"""Channel counters: one count per coincidence, read and cleared every second."""


class Counters:
    def __init__(self, channels: int) -> None:
        self.counts = [0] * channels

    def hit(self, channel: int) -> None:
        self.counts[channel] += 1

    def read_and_clear(self) -> list[int]:
        counts, self.counts = self.counts, [0] * len(self.counts)
        return counts
