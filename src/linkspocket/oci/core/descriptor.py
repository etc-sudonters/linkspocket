import dataclasses as dc
import hashlib
import io
import json as _json
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

    @staticmethod
    def from_str(s: str) -> "Digest":
        return Digest.from_hex(s[s.index(":") + 1 :])


@dc.dataclass
class Descriptor:
    """
    Represents content stored in a registry
    """

    digest: Digest
    bytes: int
    content_type: str
    content: streams.NamedReader
    annotations: T.Dict[str, str] = dc.field(default_factory=dict)

    @staticmethod
    def empty(content_type: T.Optional[str] = None) -> "Descriptor":
        if content_type is None:
            content_type = "application/vnd.oci.empty.v1+json"

        return Descriptor(
            Digest.from_hex(
                "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"
            ),
            2,
            content_type,
            streams.name("<empty>", T.cast(streams.SeekReader, io.BytesIO(b"{}"))),
        )


@dc.dataclass
class DigestStream(streams.Writer):
    """
    Treats a hashing algorithm like a write only stream
    """

    algo: _hashlib.HASH

    def write(self, b) -> int:
        self.algo.update(b)
        return len(b)

    def digest(self) -> Digest:
        return Digest(self.algo.name, self.algo.digest())


def from_str(s: str, name: str, content_type: str) -> Descriptor:
    return from_bytes(s.encode(), name, content_type)


def from_bytes(b: bytes, name: str, content_type: str) -> Descriptor:
    h = hashlib.sha256()
    h.update(b)
    return Descriptor(
        Digest(h.name, h.digest()),
        len(b),
        content_type,
        streams.name(name, T.cast(streams.SeekReader, io.BytesIO(b))),
    )


def from_stream(s: streams.NamedReader, content_type: str) -> Descriptor:
    digester = DigestStream(hashlib.sha256())
    sizer = streams.Sizer()
    tee = streams.TeeWriter(digester, sizer)
    shutil.copyfileobj(s, tee)
    s.seek(0, 0)
    return Descriptor(digester.digest(), sizer.written, content_type, s)


def from_obj(
    obj: T.Any,
    name: str,
    content_type: str,
    *,
    skipkeys=False,
    ensure_ascii=True,
    check_circular=True,
    allow_nan=True,
    cls=None,
    indent=None,
    separators=None,
    default=None,
    sort_keys=False,
    **kw,
) -> Descriptor:

    c = _json.dumps(
        obj,
        skipkeys=skipkeys,
        ensure_ascii=ensure_ascii,
        check_circular=check_circular,
        allow_nan=allow_nan,
        cls=cls,
        indent=indent,
        separators=separators,
        default=default,
        sort_keys=sort_keys,
        **kw,
    )

    return from_str(c, name, content_type)


def load_from(d: T.Dict[str, T.Any]) -> Descriptor:
    return Descriptor(
        Digest.from_str(d["digest"]),
        bytes=d["size"],
        content_type=d["mediaType"],
        content=None,
        annotations=d.get("annotations", {}),
    )
