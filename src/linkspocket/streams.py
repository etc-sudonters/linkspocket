import dataclasses as dc
import io
import typing as T


class MustCloseStream(T.Protocol):
    def close(self):
        ...


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


NamedReader = type("NamedReader", (Named, Reader), {})
NamedWriter = type("NamedWriter", (Writer, Named), {})
MustCloseReader = type("MustCloseReader", (Reader, MustCloseStream), {})


@dc.dataclass()
class TeeWriter(Writer):
    _1: Writer
    _2: Writer

    def write(self, s: T.Optional[bytes]) -> int:
        self._1.write(s)
        self._2.write(s)

        return len(s) if s is not None else 0


@dc.dataclass()
class Sizer(Writer):
    written: int = 0

    def write(self, s: T.Optional[bytes]) -> int:
        if s is None:
            return 0
        self.written += len(s)
        return len(s)


@dc.dataclass()
class TeeReader(Reader):
    _1: Reader
    _2: Reader

    def read(self, s: int = 0) -> bytes:
        r = self._1.read(s)
        self._2.read(s)
        return r


@dc.dataclass()
class _namedreader(NamedReader):
    n: str
    r: Reader

    def name(self) -> str:
        return self.n

    def read(self, s: int = 0) -> bytes:
        return self.r.read(s)


def name(n: str, r: Reader) -> NamedReader:
    return _namedreader(n, r)


class StringReader(Reader):
    r: io.BytesIO

    def __init__(self, s: str):
        self.r = io.BytesIO(s.encode())

    def read(self, s: int = 0) -> bytes:
        return self.r.read(s)


@dc.dataclass()
class FileReader(MustCloseReader):
    fh: io.BufferedReader

    def read(self, s: int = 0) -> bytes:
        return self.fh.read(s)

    def close(self):
        self.fh.close()
