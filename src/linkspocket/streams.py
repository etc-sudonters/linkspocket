import dataclasses as dc
import typing as T

class Named(T.Protocol):
    def name(self) -> str:
        ...

class Writer(T.Protocol):
    def write(self, s: T.Optional[bytes]) -> int:
        ...

class Reader(T.Protocol):
    def read(self, s: int = 0) -> bytes:
        ...

class Seeker(T.Protocol):
    def seek(self, n: int, origin: int):
        ...

class SeekReader(Seeker, Reader, T.Protocol):
    ...

class NamedReader(Named, Reader, Seeker, T.Protocol):
    ...

@dc.dataclass()
class TeeWriter(Writer):
    _1: Writer
    _2: Writer

    def write(self, b: T.Optional[bytes]) -> int:
        self._1.write(b)
        self._2.write(b)

        return len(b) if b is not None else 0

@dc.dataclass()
class Sizer(Writer):
    written: int = 0

    def write(self, b: T.Optional[bytes]) -> int:
        if b is None:
            return 0
        self.written += len(b)
        return len(b)

@dc.dataclass()
class ReadTicker(Reader):
    _tick: T.Callable[[int], None]

    def read(self, length: int = 0) -> bytes:
        self._tick(length)
        return b''

@dc.dataclass()
class TeeReader(Reader):
    _1: Reader
    _2: Reader

    def read(self, length: int = 0) -> bytes:
        r = self._1.read(length)
        self._2.read(length)
        return r

@dc.dataclass()
class _namedreader(NamedReader):
    n: str
    r: SeekReader

    def name(self) -> str:
        return self.n

    def read(self, s: int = 0) -> bytes:
        return self.r.read(s)

    def seek(self, n: int, origin: int) -> None:
        return self.r.seek(n, origin)

def name(n: str, r: SeekReader) -> NamedReader:
    return _namedreader(n, r)
