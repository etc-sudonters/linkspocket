import dataclasses as dc
import hashlib
import io
import shutil
import typing as T

import _hashlib

from ... import streams


@dc.dataclass
class Digest:
    """
    Content address for blob in registry
    """

    algo: str
    hash: bytes

    def __repr__(self) -> str:
        return f"<Digest(algo={self.algo}, hash={self.hash.hex()})>"

    def __str__(self) -> str:
        return f"{self.algo}:{self.hash.hex()}"

    @staticmethod
    def from_hex(hex: str) -> "Digest":
        return Digest("sha256", bytes.fromhex(hex))


@dc.dataclass
class Descriptor:
    """
    Represents content stored in a registry
    """

    digest: Digest
    bytes: int
    content_type: str
    annotations: T.Dict[str, str] = dc.field(default_factory=dict)

    @staticmethod
    def empty(content_type: str) -> "Descriptor":
        return Descriptor(
            Digest.from_hex(
                "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"
            ),
            2,
            content_type,
        )


@dc.dataclass
class DigestStream(io.RawIOBase):
    """
    Treats a hashing algorithm like a write only stream
    """

    algo: _hashlib.HASH

    def writable(self) -> bool:
        return True

    def write(self, b) -> T.Optional[int]:
        self.algo.update(b)
        return len(b)

    def digest(self) -> Digest:
        return Digest(self.algo.name, self.algo.digest())


def from_str(s: str, content_type: str) -> Descriptor:
    return from_bytes(s.encode(), content_type)


def from_bytes(b: bytes, content_type: str) -> Descriptor:
    h = hashlib.sha256()
    h.update(b)
    return Descriptor(Digest(h.name, h.digest()), len(b), content_type)


def from_stream(s: io.BufferedReader, content_type: str) -> Descriptor:
    digester = DigestStream(hashlib.sha256())
    sizer = streams.Sizer()
    tee = streams.Tee(digester, sizer)
    shutil.copyfileobj(s, tee)
    return Descriptor(digester.digest(), sizer.written, content_type)


def from_hex(hex: str, size: int, media_type: str) -> Descriptor:
    return Descriptor(Digest("sha256", bytes.fromhex(hex)), size, media_type)
