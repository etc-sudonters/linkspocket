import io
import dataclasses as dc

@dc.dataclass()
class Tee(io.RawIOBase):
    _1: io.RawIOBase
    _2: io.RawIOBase

    def writable(self) -> bool:
        return True

    def write(self, b: bytes) -> int:
        self._1.write(b)
        self._2.write(b)

        return len(b)

@dc.dataclass()
class Sizer(io.RawIOBase):
    written: int = 0

    def writable(self) -> bool:
        return True
    
    def write(self, b: bytes) -> int:
        self.written += len(b)
        return len(b)
