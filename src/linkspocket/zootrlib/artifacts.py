import dataclasses as dc
import enum
import io
import os
import pathlib
import re
import typing as T

_file_re = re.compile(
    r"OoT_(?P<setting>[A-Z0-9]{5})_(?P<seed>[A-Z0-9]+)_?(?P<world>W\d+)?_?(?P<kind>\w+)?"
)

class FileKind(enum.Enum):
    Cosmetic = enum.auto()
    Settings = enum.auto()
    Spoiler = enum.auto()
    Rom = enum.auto()
    Patch = enum.auto()


@dc.dataclass(frozen=True)
class ZootrFile(os.PathLike):
    kind: FileKind
    path: pathlib.Path
    world: T.Optional[int]
    settings: str
    seed: str

    def open(self) -> io.BufferedReader:
        return open(self, "rb")

    def __hash__(self) -> int:
        return hash(self.path)

    def __fspath__(self) -> str:
        return self.path.__fspath__()


def zootr_files_from_dir(d: pathlib.Path) -> T.Iterable[ZootrFile]:
    for candidate in d.glob("OoT_*"):
        if candidate.is_dir():
            continue

        if (zf := _zootr_file_from_path(candidate)) is not None:
            yield zf


def _zootr_file_from_path(fp: pathlib.Path) -> T.Optional[ZootrFile]:
    name = fp.name
    if (m := _file_re.match(name)) is None:
        return None

    return ZootrFile(
        _zootr_kind_from_str(T.cast(str, m.group("kind"))),
        fp,
        None,
        T.cast(str, m.group("setting")),
        T.cast(str, m.group("seed")),
    )


def _zootr_kind_from_str(k: str) -> FileKind:
    if k is None:
        return FileKind.Rom

    k = k.lower()

    if k == "cosmetics":
        return FileKind.Cosmetic
    if k == "settings":
        return FileKind.Settings
    if k == "spoiler":
        return FileKind.Spoiler

    raise Exception()
