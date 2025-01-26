import enum
import sys
import dataclasses as dc
import typing as T


class Canvas(enum.IntEnum):
    Foreground = 38
    Background = 48


def color(c: int, canvas: Canvas) -> str:
    return f"\033[{canvas.value}:5:{c}m"


def reset() -> str:
    return "\033[0m"


def fg(c: int) -> str:
    return color(c, Canvas.Foreground)


def bg(c: int) -> str:
    return color(c, Canvas.Background)


def resetline() -> str:
    return "\033[G\033K"


@dc.dataclass()
class Std:
    out: T.TextIO
    err: T.TextIO
    in_: T.TextIO


def newstd() -> Std:
    return Std(out=sys.stdout, err=sys.stderr, in_=sys.stdin)
