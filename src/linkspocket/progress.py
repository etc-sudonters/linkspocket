import dataclasses as dc
import io
import typing as T

from . import console as C
from . import streams


def bar(progress: float, total: float, filled: str, unfilled: str) -> str:
    """forestall + trafuri"""
    scale = 50
    percent = int(scale * progress / total)
    return (filled * percent) + (unfilled * (scale - percent))


class Render(T.Protocol):
    def tick(self, n: float) -> str:
        ...


@dc.dataclass()
class Bar(Render):
    filled: str
    unfilled: str
    length: float
    progress: float = dc.field(init=False, default=0)

    def tick(self, n: float) -> str:
        self.progress += n
        return bar(self.progress, self.length, self.filled, self.unfilled)


@dc.dataclass()
class Percentage(Render):
    total: float
    progress: float = dc.field(init=False, default=0)

    def tick(self, n: float) -> str:
        self.progress += n
        percent = (self.progress / self.total) * 100
        return f"{percent:>6.2f}%"


@dc.dataclass()
class Spinner(Render):
    states: T.Sequence[str]
    ticks: int = dc.field(init=False, default=0)

    def tick(self, _) -> str:
        self.ticks += 1
        return self.states[self.ticks % len(self.states)]


@dc.dataclass()
class Static(Render):
    s: str

    def tick(self, _) -> str:
        return self.s


@dc.dataclass()
class Many(Render):
    r: T.Sequence[Render]

    def tick(self, n: float) -> str:
        b = io.StringIO(newline=None)

        for r in self.r:
            b.write(r.tick(n))

        return b.getvalue()


@dc.dataclass()
class MinTick(Render):
    r: Render
    total: float
    min_tick: float
    progress: float = dc.field(init=False, default=0)
    ticks: float = dc.field(init=False, default=0)
    has_ticked: bool = dc.field(init=False, default=False)

    def tick(self, n: float) -> str:
        self.ticks += n
        self.progress += n
        should_tick = (
            not self.has_ticked
            or self.ticks >= self.min_tick
            or self.progress == self.total
        )

        if should_tick:
            self.has_ticked = True
            ticks = self.ticks
            self.ticks = 0
            return self.r.tick(ticks)

        return ""

@dc.dataclass()
class OnFinalTick(Render):
    r: Render
    total: float
    display: str
    progress: float = dc.field(init=False, default=0)

    def tick(self, n: float) -> str:
        self.progress += n

        if self.progress >= self.total:
            return self.display

        return self.r.tick(n)

@dc.dataclass()
class NewLineAtFinal(Render):
    total: float
    progress: float = dc.field(init=False, default=0)

    def tick(self, n: float) -> str:
        self.progress += n

        if (self.progress / self.total) >= 1:
            return "\n"
        return ""


@dc.dataclass()
class Display:
    r: Render
    w: T.TextIO

    def tick(self, n: float) -> None:
        d = self.r.tick(n)
        print(d, end="", flush=True, file=self.w)


@dc.dataclass()
class Reader(streams.Reader):
    r: streams.Reader
    d: Display

    def read(self, length: int = 0) -> bytes:
        r = self.r.read(length)
        self.d.tick(float(len(r)))
        return r


@dc.dataclass()
class Writer(streams.Writer):
    w: streams.Writer
    d: Display

    def write(self, b: bytes) -> int:
        n = self.w.write(b)
        self.d.tick(float(n))
        return n
