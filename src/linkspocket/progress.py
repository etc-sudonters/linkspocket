import dataclasses as dc
import io
import typing as T
from . import console as C

from . import streams


def bar(
    progress: float, total: float, filled: str, unfilled: str, scale: int = 100
) -> str:
    """forestall + trafuri"""
    percent = int(scale * progress / total)
    return (filled * percent) + (unfilled * (scale - percent))


class Render(T.Protocol):
    def tick(self, n: float) -> str:
        ...


@dc.dataclass()
class _progress(Render):
    total: float
    progress: float = dc.field(init=False, default=0.0)

    def tick(self, n: float) -> str:
        self.progress += n
        return ""


@dc.dataclass()
class Bar(_progress):
    filled: str
    unfilled: str

    def tick(self, n: float) -> str:
        super().tick(n)
        return bar(self.progress, self.total, self.filled, self.unfilled)


@dc.dataclass()
class Percentage(_progress):
    def tick(self, n: float) -> str:
        super().tick(n)
        percent = (self.progress / self.total) * 100
        return f"{percent:>6.2f}%"


@dc.dataclass()
class Spinner(Render):
    states: T.Sequence[str]
    ticks: int = dc.field(init=False, default=0)

    def tick(self, n) -> str:
        self.ticks += 1
        return self.states[self.ticks % len(self.states)]


@dc.dataclass()
class Static(Render):
    s: str

    def tick(self, n) -> str:
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
class MinTick(_progress):
    r: Render
    min_tick: float
    ticks: float = dc.field(init=False, default=0)
    has_ticked: bool = dc.field(init=False, default=False)

    def tick(self, n: float) -> str:
        super().tick(n)
        self.ticks += n
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
class OnFinalTick(_progress):
    r: Render
    display: str

    def tick(self, n: float) -> str:
        super().tick(n)

        if self.progress >= self.total:
            return self.display

        return self.r.tick(n)


@dc.dataclass()
class Display:
    r: Render
    w: T.TextIO

    def tick(self, n: float) -> None:
        d = self.r.tick(n)
        print(d, end="", flush=True, file=self.w)


@dc.dataclass()
class Reader(streams.NamedReader):
    r: streams.NamedReader
    d: Display

    def read(self, s: int = 0) -> bytes:
        r = self.r.read(s)
        self.d.tick(float(len(r)))
        return r

    def name(self) -> str:
        return self.r.name()


@dc.dataclass()
class Writer(streams.NamedWriter):
    w: streams.NamedWriter
    d: Display

    def write(self, s: T.Optional[bytes]) -> int:
        n = self.w.write(s)
        self.d.tick(float(n))
        return n

    def name(self) -> str:
        return self.w.name()


def track(s: streams.NamedReader, n: float, w: T.TextIO) -> Reader:
    return Reader(s, Display(ticker(s.name(), n), w))


def ticker(name: str, n: float):
    r = Many(
        [
            Static(f"{C.resetline()} "),
            Spinner(
                [
                    f"{C.fg(70)}◌{C.reset()}",
                    f"{C.fg(76)}◎{C.reset()}",
                    f"{C.fg(82)}◍{C.reset()}",
                    f"{C.fg(156)}●{C.reset()}",
                    f"{C.fg(82)}◍{C.reset()}",
                    f"{C.fg(76)}◎{C.reset()}",
                ]
            ),
            Static(f"{C.reset()} "),
            Bar(filled=f"{C.fg(129)}={C.reset()}",
                unfilled=" ", total=n),
            Static(" "),
            Percentage(n),
            Static(f" {name}"),
        ]
    )

    r = MinTick(r=r, total=n, min_tick=n * 0.032)
    r = OnFinalTick(
        r=r,
        total=n,
        display=f"{C.resetline()} {C.fg(156)}●{C.reset()} {name}" + "\n",
    )
    return r
